# Localhost Setup

- I followed this [youtube tutorial](https://youtu.be/FVumnHy5Tzo?si=GHsB3YZAU9zkXPsH)
- Create a directory called localhost in the same directory where chromedrivers were installed.
- Open command prompt and run this command to create a Chrome instance at port 9222:

```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="{localhost_dir_location}"
```

- Sign into your twitter account in the localhost Chrome window