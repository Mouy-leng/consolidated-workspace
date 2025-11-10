# Step-by-Step Guide to Deploying a Website to genxfx.org Using Namecheap Hosting and cPanel

---

## Introduction

Deploying a static website to a custom domain using shared hosting is a foundational task for web developers and site owners. For genxfx.org, leveraging Namecheap hosting paired with cPanel provides a flexible, industry-standard environment that strikes a balance between simplicity and control. This comprehensive guide will walk you through each phase of deployment, from preparing your website files and configuring DNS, to using cPanel's File Manager, adjusting file permissions, and verifying your site is live. Additionally, the report will cover alternative upload methods (FTP/SSH), highlight typical mistakes, demonstrate troubleshooting, and explain robust verification and cache-flushing techniques.

---

## Understanding the Project Output: The dist Folder Structure

Before considering deployment, it’s crucial to understand what should be uploaded. Modern web development tools (such as Vite, React, or Angular) compile source code into a distribution folder—usually named dist or build. This folder contains optimized, production-ready files.

- **Purpose of the dist Folder:** The dist ("distribution") folder includes all static files needed to run the site: typically an index.html and an assets subdirectory with JavaScript bundles, CSS, images, and other static resources. These have been minified, bundled, and are ready for deployment.

- **File Structure Example:**
  ```
  dist/
    ├── index.html
    └── assets/
          ├── app.f9c9de34.js
          ├── style.abc274e.css
          └── logo.png
  ```
  It is essential that when you upload, index.html and the assets directory both reside within the web root (public_html) on your server. Failure to do so may result in missing files, script errors, or broken styles on your deployed site.

Understanding what the dist folder contains ensures you upload the correct files and structure, preventing inadvertent breakage of your front-end application.

---

## Prerequisites for Deploying a Static Website on Namecheap

Before uploading any files or configuring settings, you must have the following prerequisites in place:

- **Active Namecheap Hosting Account:** Ensure you have a Namecheap hosting plan (shared, VPS, or reseller), and that the hosting is associated with your domain, genxfx.org.
- **Access to Domain Settings:** The ability to update DNS or nameservers for genxfx.org is critical—either within Namecheap or your existing registrar.
- **Website Build Output:** You must have run your project’s build process successfully on your local machine. For Vite/React/Vue/Angular projects, this is typically accomplished via:
  ```bash
  npm run build
  ```
  This command produces the dist directory containing deployable files. Verify your index.html and assets are present inside dist.
- **cPanel and Namecheap Account Credentials:** Keep your login details for Namecheap and cPanel at hand. These enable you to access hosting management panels for deployment.
- **Internet Connectivity and File Compression Utility:** For uploading folders (e.g., assets), it’s often more efficient to compress them into a .zip file before uploading via cPanel File Manager.

Meeting these prerequisites will ensure a smooth path through all subsequent setup and deployment steps.

---

## Step 1: Domain DNS Configuration for genxfx.org

**Objective:** Ensure that genxfx.org points to the correct hosting server (your Namecheap hosting account). Your domain settings determine where browser requests are routed.

**1.1. If Your Domain is Registered with Namecheap**

- **Automatic Assignment:** Purchasing Namecheap hosting and the domain together means Namecheap typically connects your domain to hosting automatically.
- **Manual Assignment:** If you’re using a previously-registered domain or a domain purchased elsewhere, you need to point its DNS to Namecheap’s hosting servers.
  - **Recommended Nameservers (for shared hosting):**
    ```
    dns1.namecheaphosting.com
    dns2.namecheaphosting.com
    ```
    After making changes, click the confirmation checkmark (✓) to save.
- **Propagation Delay:** DNS changes can take anywhere from a few minutes to 48 hours to propagate globally. Until propagation is complete, your website may not be immediately accessible worldwide.

**1.2. How To Change Nameservers**

- **Within Namecheap:**
  1. Login to your Namecheap dashboard.
  2. Go to the **Domain List**.
  3. Click **Manage** next to your domain.
  4. Under the **Nameservers** section, select “Namecheap Web Hosting DNS” from the dropdown menu.
  5. Save your changes.
- **From Another Registrar:**
  - Log in to your existing registrar’s control panel (e.g., GoDaddy, Google Domains).
  - Locate DNS/Nameservers settings, and input the Namecheap hosting nameservers.
  - Save changes and allow time for propagation.

**TIP:** While you wait for DNS propagation, you can still manage hosting and upload website files. It is also possible (although advanced) to view your site before DNS changes install completely by modifying your local hosts file.

**1.3. Testing DNS Propagation**

- Use an online tool such as **DNS Checker** or **Whatsmydns** to monitor if your domain is resolving to the correct Namecheap server IP globally.
- A successful lookup means requests to genxfx.org now point to your Namecheap account.

Ensuring the proper DNS configuration is foundational; if the domain doesn’t point to your hosting, your deployment will not be visible publicly.

---

## Step 2: Accessing Namecheap Hosting Dashboard and cPanel

Once your domain is linked with hosting, manage your site using Namecheap’s dashboard and cPanel, the industry-standard web control panel.

**2.1. Logging in to Namecheap**

- Visit Namecheap.com and click **Sign In**.
- Enter your username and password.

**2.2. Accessing cPanel via the Namecheap Dashboard**

1.  In the left sidebar, select **Hosting List**.
2.  Locate your relevant hosting plan and domain (genxfx.org).
3.  Click the **Go to cPanel** button for your hosting plan. This will either one-click log you in or present cPanel credentials emailed to you.

**Alternative:** Access cPanel directly via:
```
http://genxfx.org/cpanel
https://serverhostname:2083
```
(Replace `serverhostname` with your assigned server, as found in your welcome email.)

You may also use your server’s IP address, particularly before DNS is set up.

**2.3. Exploring the cPanel Interface**

On successful login, you’ll see the cPanel dashboard organized by function: Files, Databases, Domains, Email, Metrics, Security, etc. The **File Manager** icon is under the **Files** section and is the primary tool for uploading/managing site files.

Key features of cPanel’s File Manager include:

-   Visual browser-based interface for navigating directories
-   Upload/download functionality for files and compressed archives
-   File/folder creation, deletion, renaming, moving, copying
-   Built-in code/text editors
-   Permission and property modification
-   Archive extraction/compression
-   Ability to view and edit hidden files (e.g., .htaccess)

Before uploading, familiarize yourself with the File Manager layout and confirm you can locate **public_html**, the web root for your site.

---

## Step 3: Locating and Preparing Website Files (client/dist/)

**3.1. Locate Your Website Files**

On your local computer, navigate to your project’s build output directory—typically `client/dist/`.

Inside `dist`, you should see:
-   `index.html` (the main homepage file)
-   `assets/` directory (containing your JavaScript, CSS, images, fonts, etc.)

**Important:** If your build tool (e.g., Angular, React, Vite, Vue, etc.) produces different subfolders or file hierarchy, ensure you confirm the structure corresponds to the expectations of a static server (index.html in the web root, with assets correctly referenced inside it).

**Best Practice:** Test your build locally before uploading, using commands such as:
```bash
npm run preview
```
or simply double-clicking on `index.html` in the `dist/` folder to open in a browser. This can reveal missing files or broken references before deploying online.

**3.2. Compressing for Bulk Upload**

cPanel File Manager does not allow uploading entire folders. To upload a directory (like `assets/`), compress it into a `.zip` archive:

-   On **Windows:** Right-click the folder → **Send To** → **Compressed (zipped) Folder**.
-   On **macOS:** Right-click and choose "**Compress**".
-   On **Linux:** Use `zip -r assets.zip assets/` in the terminal.

Do the same for your entire `dist` folder if you plan to upload all content at once.

**TIP:** Uploading a zipped archive is often much quicker and more reliable than uploading many files individually; once uploaded, File Manager can "Extract" the archive in place.

---

## Step 4: Navigating to the public_html Directory in cPanel

**public_html** is the web root directory for your primary website in a typical cPanel hosting environment. All public-facing website files (like index.html, images, scripts, stylesheets) for genxfx.org must be placed here.

**4.1. Locating public_html**

-   In the File Manager, use the left-hand folder tree or the primary folder view to navigate to `/public_html`.
-   If subdomains or addon domains are configured, each will have its own corresponding subdirectory under `public_html` (e.g., `/public_html/addondomain.com/`). For the main domain, simply use `/public_html`.

**4.2. Understanding Folder Contents**

-   You may see a `cgi-bin` folder (for scripts, rarely used for modern static sites), placeholder files (like `default.htm` or `parking-page.shtml` from Namecheap), or other previously uploaded content.
-   It is generally safe to delete any default placeholder files before uploading your site, but always be cautious—never delete system or configuration files if uncertain on their function.

---

## Step 5: Uploading index.html and Assets Folder via File Manager

**5.1. Uploading Files/Folders**

**A. If Uploading Individual Files**

1.  Click the **Upload** button in the File Manager toolbar.
2.  A new window/tab will open. Drag and drop your `index.html`.
3.  Repeat for each file, including necessary directories (assets, images, etc.). However, folders must be zipped for upload, as File Manager will only accept file uploads.

**B. Bulk Upload via ZIP Archive (Recommended for Folders)**

1.  Compress your `client/dist/` directory contents into a `.zip` file. For example, select `index.html` and the `assets` folder, right-click, and select **Compress** or **Send to Zip**.
2.  In File Manager, select the **Upload** button and upload the `.zip` archive.
3.  Once upload is complete (wait for the 100% green progress bar), return to File Manager and refresh the view if the file doesn’t appear immediately.
4.  Right-click the uploaded `.zip` file.
5.  Select **Extract**. Extract files directly into `/public_html` (not into a subfolder unless desired).
6.  After extraction, you will see `index.html` and the `assets` folder under `/public_html`.
7.  Once confirmed, you can safely delete the original zip file to conserve server space.

**5.2. Drag-and-Drop from Local System**

If uploading a small number of files, you may drag-and-drop directly into the upload area in File Manager. However, drag-and-drop does not work for folders unless zipped.

**5.3. Extracting and Organizing Files**

Post-extraction, confirm the following:
-   `index.html` is at `/public_html/index.html`
-   `assets/` (and any subfolders) is directly within `public_html`, not in a subfolder like `/public_html/dist/assets/`
-   Paths in `index.html` refer correctly to `assets/...` and not to a different directory level

**5.4. Replacing Placeholder Files**

Delete any default files such as `index.html`, `default.htm`, or `parking-page.shtml` present from the initial cPanel setup, when you are ready for your new site to go live.

**5.5. Pro Tip: Extracting Directories**

For large projects, extracting the whole `dist` structure is more efficient because browsers will load all necessary JS/CSS/images from the correct locations. Only extract directly within `public_html`; moving folders after extraction increases the risk of misplacement or lost file references.

---

## Step 6: Alternative Upload Methods

While the cPanel File Manager is the easiest, there are other ways to upload site files, especially for advanced users or with high file volume.

**6.1. Using FTP (FileZilla)**

**When to use FTP:** If you need to upload a large number of files quickly, or frequently update website content.

**Setting Up FileZilla**
1.  Download **FileZilla** and install it.
2.  Obtain your FTP credentials from the Namecheap hosting dashboard or your account’s setup email.
    -   **Host:** Your domain name, cPanel server hostname, or server IP (e.g., `genxfx.org` or `s99.web-hosting.com`)
    -   **Username:** Your cPanel username (found in account details)
    -   **Password:** Your cPanel account password
    -   **Port:** `21` for FTP (or `21098` for SFTP over SSH)
3.  For added security, use SFTP (correct port and protocol settings).

**Connecting and Uploading**
-   In FileZilla, enter the credentials and click **Quickconnect**.
-   You will see your local files on the left and server files on the right. Navigate to `/public_html` on the server side.
-   Select your local `index.html` and `assets` folder (or entire `dist` contents), drag and drop to the right panel to upload.
-   Wait for the transfers to complete successfully.

**Note:** FileZilla supports uploading folders directly, and bulk transfers work faster and more reliably compared to browser-based single file uploads. However, FTP clients cannot extract zip files server-side—such archives must be extracted in cPanel File Manager after upload if needed.

**6.2. Using SSH and wget in cPanel Terminal**

**When to use:** For advanced users or when you need to upload directly from another server or cloud (or for downloading large archives via URL).

**Accessing SSH/Terminal in cPanel**
1.  In cPanel, locate the **Terminal** option (under the **Advanced** section).
2.  The first time you open it, accept the disclaimer.

**Uploading Using wget**
1.  If you have your zip/bundle at a public URL (like a cloud storage direct link or another server), use:
    ```bash
    wget https://example.com/dist.zip
    ```
    (Make sure you're in `/home/username/public_html` before downloading.)
2.  Once downloaded, use the built-in terminal’s `unzip` or File Manager’s extract function to unpack the files.
3.  Remove the archive after extraction to save space.

SSH/Terminal access is powerful but should be reserved for advanced users. Always ensure that you are not overwriting site-critical files.

---

## Step 7: Setting Correct File Permissions in public_html

Correct file permissions are essential for both security and proper functioning of your website. Incorrect permissions can result in errors such as **403 Forbidden** or **500 Internal Server Errors**.

**7.1. Default Permissions**

-   `public_html` directory: `750` or `755`
-   All subdirectories (including `assets/`): `755`
-   All files (such as `index.html`, JS/CSS): `644`
-   Sensitive files (e.g., configuration or `.htaccess`): `644` (or more strict if required)

**7.2. How to Check and Set Permissions**

**Using File Manager**

1.  In cPanel File Manager, view the **Permissions** column.
2.  Right-click any file or folder → **Change Permissions**.
3.  Set directories to `755` (owner: read, write, execute | group: read, execute | public: read, execute).
4.  Set files to `644` (owner: read, write | group: read | public: read).
5.  Apply changes as needed.

**Using SSH**

If you’re confident with command line:
```bash
cd /home/username/public_html

# Set directories to 755
find . -type d -exec chmod 755 {} \;

# Set files to 644
find . -type f -exec chmod 644 {} \;
```
Always double-check ownership and not to change the home directory permissions as it may disrupt cPanel functionality.

**7.3. Why Permissions Matter**

-   **Too strict** (e.g., `600` on files): Public visitors get 403 errors.
-   **Too lax** (e.g., `777`): Security risk; files/folders can be modified by anyone.

Reset permissions whenever you mass-upload via FTP or archives as extracted files may retain their previous permissions from local machine or source.

---

## Step 8: Enabling and Editing .htaccess in File Manager

The `.htaccess` file allows you to customize server behavior for your static site—redirects, custom error pages, URL rewrites, and cache headers. Some JavaScript frameworks (especially SPAs, React, Vue, Angular) require an `.htaccess` rewrite rule to handle client-side routing (so that refreshing a subpage URL loads `index.html`).

**8.1. Making .htaccess Visible**

By default, files starting with a dot (`.`, called dotfiles) are hidden in File Manager. Enable dotfiles visibility:

-   In File Manager, click **Settings** (top right).
-   Check “**Show Hidden Files (dotfiles)**”.
-   Save.

You can now view and edit `.htaccess` in `/public_html`.

**8.2. Typical Rewrite Rule for SPAs**

If your app uses client-side routing (e.g., React/Vue/Angular):

1.  Create a new file named `.htaccess` (if it doesn’t exist).
2.  Edit and insert:
    ```
    RewriteEngine On
    RewriteBase /
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteCond %{REQUEST_FILENAME} !-l
    RewriteRule . /index.html [L]
    ```
3.  Save changes.

This ensures direct access to subpaths on your domain (like `/about` or `/dashboard`) always returns `index.html`.

**8.3. Caching and .htaccess**

To avoid old files being served after a new deployment, add cache headers for static assets in `.htaccess` (advanced) or ensure assets are built with unique hashes in filenames—this is automatic with modern build tools (Webpack, Vite, etc.).

---

## Step 9: Common Pitfalls and Mistakes to Avoid

Deploying a static site can be straightforward, but common mistakes can lead to errors or broken sites. Be aware of these issues and how to prevent them:

**9.1. Uploading Inside a Subfolder**

-   **Mistake:** Extracting/uploading files into `/public_html/dist/` instead of directly into `/public_html/`.
-   **Consequence:** Site only loads at `genxfx.org/dist/` or not at all.
-   **Fix:** Move all contents of the `dist` directory (`index.html` and `assets`) to `/public_html`.

**9.2. Not Removing Placeholder Files**

-   Old files such as `index.html`, `default.htm`, or `parking-page.shtml` can cause cPanel’s default page or a parking/coming soon page to display instead of your actual site.

**9.3. Permissions Set Too Strict or Too Open**

-   Setting all files and directories to `777` is a major security risk; setting them to `600` or `400` makes them inaccessible.

**9.4. Broken Asset References**

-   If `index.html` references `/dist/assets/...` but you upload only `assets/` directly under `public_html`, assets may load from wrong paths.
-   Use relative paths or double-check asset URLs in your build settings before deploying.

**9.5. Failing to Clear Cache**

-   Browsers may aggressively cache old assets, causing new deployments to appear “unchanged” for users. Solution: Use file hashes in filenames (handled by your build tool) and, for immediate visibility, perform a hard refresh (`Ctrl + Shift + R`) after deployment.

**9.6. Not Extracting Zipped Folders**

-   Directly uploading a zipped folder without extracting means files won’t be served. Always extract and check the final folder structure.

**Summary Table: Deployment Pitfalls and Solutions**

| Mistake | Symptom | Solution |
| :--- | :--- | :--- |
| Uploading into `/dist/` not `/public_html/` | Site not reachable/root URL empty | Move files to `/public_html` |
| Not deleting default/parking placeholders | See default or parking page | Remove default/parking files |
| Incorrect file/folder permissions | 403/500 errors, "not found" | Set files: `644`, dirs: `755` |
| Broken assets links | Missing images/scripts | Check/correct asset paths |
| Not extracting zip archives | Zip file visible, site broken | Extract archives post-upload |
| Not clearing browser cache | New site not visible | Hard refresh, hashed filenames |

---

## Step 10: Verifying Deployment and Checking Website Live Status

Once you have uploaded all your files and configured the server, the final step is to verify that your website is live and accessible to the public.

**10.1. Visiting Your Domain**

-   Open a new browser window (preferably in incognito or private mode to avoid cached results).
-   Navigate to your domain: `http://genxfx.org`.
-   Your website should load correctly.

**10.2. Performing a Hard Refresh**

-   If you see an old version of your site or a placeholder page, your browser might be serving a cached version.
-   Perform a hard refresh:
    -   **Windows/Linux:** `Ctrl + Shift + R`
    -   **macOS:** `Cmd + Shift + R`
-   This forces the browser to re-download all assets from the server.

**10.3. Checking Browser Developer Tools**

-   Open your browser's developer tools (usually by pressing `F12` or right-clicking and selecting "Inspect").
-   Go to the **Network** tab.
-   Refresh the page. Check for any failed requests (highlighted in red). A 404 error indicates a missing file, often due to an incorrect path or a file that wasn't uploaded.
-   Go to the **Console** tab. Look for any JavaScript errors that might be preventing your application from running correctly.

**10.4. Using an Online Tool to Check Global Availability**

-   Use a tool like `whatsmydns.net` or `dnschecker.org` to confirm that your domain's DNS has propagated globally and is pointing to your Namecheap server's IP address.
-   Use a website availability checker like `downforeveryoneorjustme.com` to ensure your site is accessible from different locations.

---

## Step 11: Post-Deployment and Maintenance

Congratulations, your website is now live! Here are a few final considerations:

**11.1. Setting Up SSL (HTTPS)**

-   Security is crucial. In your cPanel, find the "SSL/TLS Status" or "Let's Encrypt SSL" tool.
-   Issue and install a free SSL certificate for your domain. This will enable HTTPS, encrypt traffic, and show a padlock icon in the browser's address bar.
-   You may need to add a rule to your `.htaccess` file to force all traffic to use HTTPS.

**11.2. Regular Backups**

-   cPanel provides backup tools. Regularly back up your `public_html` directory and any databases. This will protect you from data loss.

**11.3. Monitoring**

-   Keep an eye on your website's performance and uptime. There are many free and paid services that can monitor your site and alert you if it goes down.

By following this comprehensive guide, you have successfully deployed your static website to `genxfx.org` using Namecheap and cPanel.