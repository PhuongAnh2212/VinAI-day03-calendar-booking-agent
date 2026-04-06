require("dotenv").config();
const express = require("express");
const { google } = require("googleapis");
const mongoose = require("mongoose");
const crypto = require("crypto");

const app = express();
app.use(express.json()); // Middleware to parse JSON bodies

const PORT = process.env.PORT || 3000;

// ==========================================
// 1. Database & Schema Setup (MongoDB)
// ==========================================
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("✅ Connected to MongoDB Atlas"))
  .catch((err) => console.error("❌ MongoDB connection error:", err));

const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  encryptedTokens: { type: String, required: true },
  iv: { type: String, required: true },
});

const User = mongoose.model("User", userSchema);

// ==========================================
// 2. Security / Encryption Utilities
// ==========================================
const ALGORITHM = "aes-256-cbc";
const ENCRYPTION_KEY = Buffer.from(process.env.ENCRYPTION_KEY, "hex");

function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(ALGORITHM, ENCRYPTION_KEY, iv);
  let encrypted = cipher.update(text, "utf8", "hex");
  encrypted += cipher.final("hex");
  return { iv: iv.toString("hex"), encryptedData: encrypted };
}

function decrypt(encryptedData, ivHex) {
  const iv = Buffer.from(ivHex, "hex");
  const decipher = crypto.createDecipheriv(ALGORITHM, ENCRYPTION_KEY, iv);
  let decrypted = decipher.update(encryptedData, "hex", "utf8");
  decrypted += decipher.final("utf8");
  return decrypted;
}

// ==========================================
// 3. Google OAuth2 Configuration
// ==========================================
const oAuth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  process.env.GOOGLE_REDIRECT_URI,
);

// Updated scopes: Allow creating events and fetching email
const SCOPES = [
  "https://www.googleapis.com/auth/calendar.events",
  "https://www.googleapis.com/auth/calendar.readonly",
  "https://www.googleapis.com/auth/userinfo.email",
];

// ==========================================
// 4. Routes: Auth & Onboarding
// ==========================================

// Generate login link
app.get("/auth", (req, res) => {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: "offline",
    scope: SCOPES,
    prompt: "consent", // Forces Google to send a refresh token every time
  });
  res.send(
    `<h1>Đăng nhập để Agent truy cập lịch của bạn:</h1><a href="${authUrl}">Nhấn vào đây để cấp quyền</a>`,
  );
});

// OAuth Callback
app.get("/oauth2callback", async (req, res) => {
  const { code } = req.query;
  try {
    const { tokens } = await oAuth2Client.getToken(code);
    oAuth2Client.setCredentials(tokens);

    // Get user email
    const oauth2 = google.oauth2({ version: "v2", auth: oAuth2Client });
    const userInfo = await oauth2.userinfo.get();
    const userEmail = userInfo.data.email;

    // Encrypt the tokens object
    const stringifiedTokens = JSON.stringify(tokens);
    const { iv, encryptedData } = encrypt(stringifiedTokens);

    // Upsert into MongoDB
    await User.findOneAndUpdate(
      { email: userEmail },
      { email: userEmail, encryptedTokens: encryptedData, iv: iv },
      { upsert: true, new: true },
    );

    res.send(
      `<h1>Thành công!</h1><p>Đã lưu token an toàn cho: <strong>${userEmail}</strong>.</p>`,
    );
  } catch (error) {
    console.error("Callback error:", error);
    res.status(500).send("Lỗi khi lấy token: " + error.message);
  }
});

// ==========================================
// 5. Routes: Booking Logic API
// ==========================================
app.post("/book-meeting", async (req, res) => {
  const { targetEmail, startTime, endTime } = req.body;

  if (!targetEmail || !startTime || !endTime) {
    return res
      .status(400)
      .json({ status: "error", reason: "Missing required fields" });
  }

  try {
    // 1. Retrieve user from database
    const user = await User.findOne({ email: targetEmail });
    if (!user) {
      return res
        .status(404)
        .json({ status: "error", reason: "User not found in database" });
    }

    // 2. Decrypt tokens and configure Google Calendar client
    const decryptedTokensStr = decrypt(user.encryptedTokens, user.iv);
    const tokens = JSON.parse(decryptedTokensStr);

    const client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI,
    );
    client.setCredentials(tokens);
    const calendar = google.calendar({ version: "v3", auth: client });

    // 3. Check FreeBusy status
    const freeBusyReq = {
      resource: {
        timeMin: startTime, // Should be ISO String (e.g., "2023-10-01T10:00:00Z")
        timeMax: endTime,
        timeZone: "UTC",
        items: [{ id: "primary" }], // Checking the user's main calendar
      },
    };

    const freeBusyRes = await calendar.freebusy.query(freeBusyReq);
    const busySlots = freeBusyRes.data.calendars["primary"].busy;

    // 4. If BUSY: Return not ok
    if (busySlots && busySlots.length > 0) {
      return res.json({ status: "not ok" });
    }

    // 5. If FREE: Create the calendar event
    const event = {
      summary: "Scheduled Meeting via Agent",
      description: "Auto-generated meeting.",
      start: { dateTime: startTime },
      end: { dateTime: endTime },
      attendees: [{ email: targetEmail }],
    };

    await calendar.events.insert({
      calendarId: "primary",
      resource: event,
      sendUpdates: "all", // Sends an email notification to the attendee
    });

    return res.json({ status: "ok" });
  } catch (error) {
    console.error("Booking error:", error);
    return res.status(500).json({
      status: "error",
      reason: error.message || "Internal Server Error",
    });
  }
});

// ==========================================
// 6. Start Server
// ==========================================
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
