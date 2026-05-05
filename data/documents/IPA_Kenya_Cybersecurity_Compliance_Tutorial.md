# IPA Kenya — Cybersecurity Compliance Step-by-Step Tutorial

This compliance program was initiated by **Peter (Deputy Country Director)** and is led by **Brian (IT / Technology Team)**. The goal is to safeguard organizational data — including **Personally Identifiable Information (PII)** of survey respondents — in line with IPA's data protection obligations. All four measures below are **mandatory** for every IPA Kenya staff member. Non-compliance will be identified through monthly and quarterly checks.

---

## Step 1 — Enable BitLocker Disk Encryption (Laptops)

> Part of IPA Kenya Cybersecurity Compliance — Step 1 of 4

BitLocker locks all data on your laptop's hard drive. If your laptop is ever lost or stolen, nobody can read your files without your password — protecting you, your colleagues, and the people we work with. BitLocker is **mandatory** on all IPA Kenya laptops.

**How to check if BitLocker is already on:**

1. Click the **Start button** (Windows logo) at the bottom-left of your screen.
2. Type **"BitLocker"** in the search bar and press **Enter**.
3. You will see a window titled **"Manage BitLocker"**. Look next to your main drive (usually **C:**).
4. Check the status:
   - **"BitLocker On"** — you are protected.
   - **"BitLocker Off"** — contact **Brian immediately**.

**If BitLocker is OFF:** Do not try to turn it on yourself. Contact Brian from the Technology Team right away so he can safely enable it without affecting your existing files. Brian will use the **Bitdefender Encryption Report** to track which laptops are compliant. Your laptop will be checked during monthly randomized staff checks.

---

## Step 2 — Set Up Windows PIN & Password (Laptops)

> Part of IPA Kenya Cybersecurity Compliance — Step 2 of 4

A PIN and password are the first barriers stopping anyone from accessing your laptop. Think of them as the lock on your front door — without them, anyone who picks up your laptop can walk straight in. Both a **PIN** and a **password** are required on all IPA Kenya laptops.

**Set up or verify your Windows PIN:**

1. Click **Start → Settings** (the gear icon).
2. Select **"Accounts"**, then click **"Sign-in options"** from the left menu.
3. Under **"PIN (Windows Hello)"**, click **"Add"** (or **"Change"** if you already have one).
4. Create a **4–6 digit PIN**. Choose something memorable but **not obvious** (not `1234` or your birth year).
5. Once set, you'll use this PIN every time you unlock your laptop.

**Set up or check your Windows Password:**

1. Go to **Settings → Accounts → Sign-in options**.
2. Under **"Password"**, click **"Add"** if you don't have one, or **"Change"** to update it.
3. Choose a **strong password**: use a mix of letters, numbers, and symbols (e.g. `Kenya@2024!`).
4. Ensure your screen locks automatically after inactivity: go to **Settings → Personalization → Lock screen → Screen timeout**.

**PIN & Password quick tips:**

- **Do** use a PIN that only you know. **Don't** use `1234`, `0000`, or your birth date.
- **Do** use a password with letters, numbers & symbols. **Don't** use your name or `password`.
- **Do** lock your screen when you step away (**Win + L**). **Don't** write your PIN/password on paper near the laptop.
- **Do** change your password if you think someone knows it. **Don't** share your login details with anyone.

Brian will conduct monthly randomized checks to verify that both a PIN and a password are active. Remote staff will be checked via Microsoft Teams.

---

## Step 3 — Set Up Cryptomator & Use Box Secure Folders (All Project Teams)

> Part of IPA Kenya Cybersecurity Compliance — Step 3 of 4

Project files often contain sensitive information about the people we work with (PII). Storing files in an encrypted Box vault means only authorized team members can open them — even if someone gains access to your Box account. All project teams **must** store files inside their team's Cryptomator vault.

**What is Cryptomator?** Cryptomator is a free app that creates a **secure, encrypted vault** inside your Box folder. Think of it as a locked safe inside your filing cabinet. Files placed inside the vault are scrambled and unreadable to anyone without the vault password.

**How to open your encrypted vault:**

1. Open the **Cryptomator app** on your laptop (ask **Brian** to install it if you don't have it).
2. You will see a list of vaults. Click on your **project vault** (e.g. "Kenya Project Files").
3. Click **"Unlock Vault"** and enter the vault password. Your team lead or Brian will provide this.
4. A **new drive** will appear on your computer (like a USB). This is your secure workspace — save and open all project files here.
5. When you are done working, click **"Lock Vault"** in Cryptomator to re-secure your files.

**File storage rules:**

- **Always** save project files inside your team's encrypted Cryptomator vault in Box.
- **Never** save respondent data, survey forms, or any PII in regular (unencrypted) Box folders.
- **Lock** your vault when you finish working. Do not leave it unlocked when not in use.
- **Report** unsecured folders to the Data Team immediately.
- **Ask** your supervisor if you're unsure which folder to use.
- **Never** share the vault password over chat or email.
- **Never** store respondent data on your Desktop or Downloads folder.

The Data Team conducts **quarterly randomized checks** to verify that all project teams are storing files in secured folders. Unsecured usage will be flagged and escalated.

---

## Step 4 — Secure Your Field Tablet (Tablet Users)

> Part of IPA Kenya Cybersecurity Compliance — Step 4 of 4

Work tablets are used in the field for data collection. Even though **SurveyCTO** protects respondent identities using a **case-based identifier system** (meaning respondents' PII such as names, ID numbers, or location is **NOT visible** on the tablet during data collection), tablets must still be kept secure to prevent unauthorized access or misuse.

**Required tablet settings:**

1. **Screen Lock** — Set a PIN or password. Auto-lock after **1–2 minutes** of inactivity.
2. **Camera Access** — Disable or restrict the camera app. Ask Brian if you're unsure how.
3. **App Store Access** — Restrict App Store / Google Play access to IT staff only. Do **not** install any new apps.
4. **Bluetooth & Wi-Fi** — Turn off Bluetooth when not in use. Only connect to **trusted** Wi-Fi networks (mobile hotspot or office network).
5. **No Personal Use** — Work tablets are for IPA work only — no personal social media, browsing, or messaging.

**Field safety rules:**

- **Do** keep the tablet locked when not actively collecting data. **Don't** install any apps or games on work tablets.
- **Do** return the tablet to your supervisor after each field day. **Don't** let community members or respondents handle the tablet.
- **Do** report a lost or stolen tablet to IT immediately. **Don't** take personal photos or videos on a work tablet.
- **Do** charge the tablet using the official charger provided. **Don't** connect to unknown or public Wi-Fi networks.

**Lost or stolen tablet:** If a tablet is lost or stolen during fieldwork, report it **immediately** to your **supervisor** and the **Admin and Security team (Mary Ateto)**. You can also reach support at **bthuo@poverty-action.org** or **support@poverty-action.org**.

---

## Compliance Checks & Enforcement

Compliance is **not optional**. The following checks are in place to verify that all staff meet the security requirements:

| Check | Frequency | Owner | Method |
|-------|-----------|-------|--------|
| Laptop encryption + PIN/Password verification | Monthly | Brian (Technology Team) | Randomized checks of 3 staff members |
| Remote staff compliance | Monthly | Brian (Technology Team) | Microsoft Teams verification |
| Box secured folder usage | Quarterly | Data Team (Vitallis) | Randomized compliance checks |
| Bitdefender Encryption Report review | Ongoing | Brian (Technology Team) | Automated reporting |

**Consequences of non-compliance:**

- **First occurrence:** Verbal reminder from the Technology Team with a 5-business-day window to resolve the issue.
- **Second occurrence:** Written notification to you and your supervisor with a 3-business-day deadline.
- **Repeated non-compliance:** Escalated to the Deputy Country Director (Peter) and may affect performance reviews.

**Remediation:** If you are flagged for non-compliance, contact Brian immediately for assistance in resolving the issue within the deadline.

---

## Security Incident Reporting

A **security incident** is any event that compromises the confidentiality, integrity, or availability of organizational data or devices. You **must** report incidents promptly — delayed reporting can worsen the impact.

**What counts as a security incident:**

- Lost or stolen laptop, tablet, or USB drive
- Unauthorized person accessing or attempting to access a device or account
- Suspicious email, phishing attempt, or unexpected login prompt
- Accidental sharing of PII or confidential data to the wrong person
- Discovery of malware, ransomware, or unusual device behavior
- BitLocker being disabled or showing "BitLocker Off" without your action
- Cryptomator vault password compromised or shared

**How to report an incident:**

1. **Immediately** notify your **supervisor** and **Brian (Technology Team)** via Microsoft Teams or email.
2. For lost/stolen devices, also notify **Mary Ateto (Admin & Security)**.
3. Do not attempt to fix the issue yourself (e.g., do not wipe the device, do not click suspicious links).
4. Provide as much detail as possible: what happened, when, which device, what data may be affected.
5. The Technology Team will assess severity and initiate the appropriate response within **24 hours**.

**Response timeline:** Critical incidents (active data breach, lost device with PII) receive a response within **4 hours**. Non-critical incidents receive a response within **24 hours**.

---

## Software & App Policy

All software and apps on IPA Kenya work devices must be approved and managed by the Technology Team.

**Approved software on laptops:**

- **Bitdefender** (antivirus/encryption monitoring — installed and managed by IT)
- **Cryptomator** (file encryption for Box vaults)
- **Microsoft Office 365** (Word, Excel, PowerPoint, Outlook, Teams)
- **SurveyCTO** / **ODK** (data collection)
- **Stata** / **R** / **Python** (analysis tools — as approved by your project)

**Approved apps on tablets:**

- **SurveyCTO** (data collection)
- **Google Maps** (navigation — field use only)
- **Camera** (only if required by project protocol and enabled by IT)

**Strictly forbidden on all work devices:**

- Personal social media apps (WhatsApp personal, Facebook, Instagram, TikTok, etc.)
- Unapproved VPN or proxy tools
- Pirated or cracked software of any kind
- File-sharing apps (Torrent, Mega, etc.)
- Personal email clients configured without IT approval

**Software updates:** Bitdefender and operating system updates are managed centrally by IT. Do not defer or cancel scheduled updates. If an update prompt appears, allow it to install. If updates fail or cause issues, contact Brian.

---

## Troubleshooting Common Issues

**BitLocker issues:**

- **BitLocker shows "Off" and I can't enable it:** Contact Brian — do not attempt to enable it yourself. IT must manage the encryption key.
- **BitLocker recovery key prompt on startup:** This can happen after a hardware change or BIOS update. Contact Brian with your laptop serial number.
- **"BitLocker waiting for activation" message:** The encryption is in progress. Leave the laptop powered on and plugged in until it completes (can take several hours).

**PIN & Password issues:**

- **Forgot my Windows PIN:** On the lock screen, click "Sign-in options" and select Password instead. Then go to Settings → Accounts → Sign-in options → PIN → "I forgot my PIN" to reset it.
- **Forgot my Windows password:** Contact Brian. He can initiate a password reset through the admin portal.
- **Screen not auto-locking:** Go to Settings → Accounts → Sign-in options and ensure "Require Windows Hello sign-in" is enabled. Also check Settings → System → Power & battery → Screen and sleep for timeout settings.

**Cryptomator issues:**

- **"Vault password incorrect" error:** Double-check the password (passwords are case-sensitive). If you've truly lost it, contact your team lead or Vitallis (Data Team). There is no way to recover a lost vault password — the vault must be recreated.
- **Vault not appearing in Cryptomator:** Re-add the vault by clicking "Add existing vault" and navigating to the vault folder in Box.
- **Can't see the unlocked vault drive:** After unlocking, the vault appears as a new drive letter (e.g. V:) in File Explorer. If it doesn't appear, try locking and unlocking again. Contact Brian if the issue persists.

**Tablet issues:**

- **Tablet won't auto-lock:** Go to Settings → Display → Screen timeout and set it to 1–2 minutes. On Samsung tablets, also check Settings → Lock screen → Secure lock settings → "Lock instantly with side key."
- **Can't restrict camera or app store:** Contact Brian. These restrictions are managed through device administration settings that IT configures.
- **SurveyCTO app crashing:** Ensure the app is updated to the latest version. If issues persist, contact the Data Team.

---

## Frequently Asked Questions

**Q: Is BitLocker mandatory even if I work from home?**
A: Yes. BitLocker protects your data regardless of where you work. All IPA Kenya laptops must have BitLocker enabled.

**Q: Can I use the same PIN for my laptop and my phone?**
A: It's not recommended. Use a different PIN for your work laptop. If one is compromised, the other remains secure.

**Q: What if my vault password expires or I forget it?**
A: There is no password recovery for Cryptomator vaults — the encryption is designed that way for security. If you lose your vault password, contact your team lead or Vitallis immediately. A new vault will need to be created and your team lead can help transfer files.

**Q: Can I access my encrypted Box files from my personal phone or home computer?**
A: No. Cryptomator vaults are device-specific. Only IPA-managed devices with Cryptomator installed can unlock and access vault files.

**Q: What happens during a compliance check?**
A: Brian or a member of the Technology Team will verify that BitLocker is active, a PIN and password are set, and your Box vault is in use. Remote staff are verified via a quick Microsoft Teams screen-share. The check takes about 5 minutes.

**Q: I received a suspicious email asking for my login details. What should I do?**
A: Do not click any links or reply. Report it immediately to Brian (Technology Team). This is a potential phishing attempt and should be reported as a security incident.

---

## Glossary

- **BitLocker** — A built-in Windows feature that encrypts (scrambles) all data on your hard drive. Without your password or recovery key, the data is unreadable even if the drive is removed from the laptop.
- **Cryptomator** — A free, open-source application that creates encrypted vaults (secure folders) for storing files. Files inside a vault are encrypted and can only be read after unlocking the vault with a password.
- **Vault** — A secure, encrypted folder created by Cryptomator. When unlocked, it appears as a separate drive on your computer where you can save and open project files. When locked, the files inside are unreadable.
- **PII (Personally Identifiable Information)** — Any data that could identify a specific person, such as names, ID numbers, phone numbers, addresses, or survey responses linked to individuals. IPA is legally obligated to protect PII.
- **Bitdefender** — The antivirus and security software installed on all IPA Kenya laptops. It monitors encryption status, scans for malware, and reports compliance to the Technology Team.
- **SurveyCTO** — The data collection platform used by IPA for field surveys. It uses a case-based identifier system so that respondents' PII is not visible on tablets during data collection.
- **Encryption** — The process of converting data into a scrambled format that can only be read by someone with the correct key or password. BitLocker encrypts your entire hard drive; Cryptomator encrypts individual folders.
- **Phishing** — A fraudulent attempt (usually via email) to trick you into revealing sensitive information such as passwords or clicking on malicious links. Always report suspicious emails to the Technology Team.
# How to Create a Procurement Request

This guide explains how to submit a procurement request using IPA's ProcessMaker system.

---

## Resources

**For more guidance, see:**

- [Procurement Policy](https://ipastorage.box.com/s/mrrn7a3rnlqb7deoz6w516285n...)
- [Training/Guidance Folder](https://ipastorage.box.com/s/lcu0wirx824e2n0i2157uzkvav...)

**For support, contact:**

- <globaloperations@poverty-action.org>

---

## Step-by-Step Instructions

### Step 1: Access ProcessMaker

Starting from Okta/Entra, click on the **ProcessMaker / IPA Digital Processes Center** icon.

### Step 2: Time Zone Notification (If Applicable)

If you haven't visited ProcessMaker recently, you may see a time zone selection screen.

> **Note:** The time zone selected does not affect how the tool functions. You may click "Ok" to proceed even if the time zone is not correct.

### Step 3: Open Procurement Center

Click **"Procurement Center"**

The Procurement Center will open in a new window.

### Step 4: Create New Request

Click **"CREATE REQUEST"**

### Step 5: Enter Request Summary

Some of your information will be auto-entered.

In the **"Request Summary"** field, enter a short (about 1-4 words) summary of what you want to buy.

### Step 6: Select Delivery Date

Select a delivery date.

**⚠️ Important Timing Requirements:**

- **Level 1 requests:** Must be at least one business week away
- **Level 2 requests:** Must be at least two business weeks away

### Step 7: Select Delivery Location

Choose the appropriate **Delivery Location** from the dropdown menu.

### Step 8: Add Item to Request

Click **"Add Item"**

### Step 9: Choose Grant Allocation

Choose the **Grant Allocation** to which this item should be charged.

> **Note:** The list of Grant Allocations available to you is based on Replicon data. If you don't see the code you need to charge to, contact your Grants Manager or <grants@poverty-action.org>.
>
> **💡 Tip:** If you are unsure about any of the items in this interface, especially GL Code, PA Code, and Estimated Price, ask your CO Procurement Administrator or <globaloperations@poverty-action.org>.

### Step 10: Select GL Code

Select the appropriate **GL Code**.

**Need help?** Contact your CO Finance person or <apinbox@poverty-action.org> with questions.

### Step 11: Select PA Code

Select the appropriate **PA Code**.

**Need help?** Contact your CO Finance person or <apinbox@poverty-action.org> with questions.

### Step 12: Write Item Description

Write a brief (usually less than 1 sentence) description of what you need.

### Step 13: Select Unit of Measure

Select the appropriate **Unit of Measure** from the dropdown menu.

### Step 14: Enter Quantity

Enter the **Quantity** needed.

### Step 15: Enter Estimated Price

Enter an **Estimated Price**.

**Need help?** Your country/regional procurement officer or <globalops@poverty-action.org> can help if you're not sure.

### Step 16: Save Item

Click **"Save changes to Item"**

### Step 17: Submit Request

Click **"Submit for Approval"**

---

## What Happens Next?

✅ **Your request has been submitted!**

### Confirmation and Next Steps

1. **Immediate:** You will receive a confirmation email right away.

2. **Over the next week:** Continue to watch your inbox carefully. As your request is reviewed and processed, you will receive more emails telling you what to do next.

---

## Need Help?

If you have questions or need assistance at any point in the process, contact:

- **General support:** <globaloperations@poverty-action.org>
- **Grant allocation questions:** Your Grants Manager or <grants@poverty-action.org>
- **Finance questions (GL Code, PA Code):** Your CO Finance person or <apinbox@poverty-action.org>
- **Procurement questions:** Your CO Procurement Administrator or <globaloperations@poverty-action.org>





---

## Need Help?

| Issue | Contact |
|-------|---------|
| BitLocker not enabled, PIN/Password setup, tablet restrictions | **Brian (Technology Team)** — Microsoft Teams or email |
| Cryptomator access, vault password, Box folder questions | **Vitallis (Data Team)** or **Brian (Technology Team)** |
| Lost or stolen device | Your **supervisor** and **Mary Ateto (Admin & Security)** |
| Suspicious email or phishing attempt | **Brian (Technology Team)** — report immediately |
| Software installation requests | **Brian (Technology Team)** — all software must be approved by IT |

Support emails: **bthuo@poverty-action.org** | **support@poverty-action.org**

---

*IPA Kenya — Cybersecurity Awareness Series | For Internal Use Only*
