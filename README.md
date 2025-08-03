FadedBalancerOFX

A DaVinci Resolve DCTL OFX plugin for adjusting channel balance and compensating for color fading or imbalances in film scans. While it does not recover lost color data, it improves visual accuracy and prepares faded footage for restoration or access.

⸻

Version

v1.0.0
	•	Works on Windows
	•	macOS compatibility in progress
	•	Linux not yet tested

⸻

Features
	•	Channel balance controls for Red, Green, and Blue (Lift, Gamma, Gain, Offset)
	•	Channel copy toggles (e.g., copy Red to Blue, Green to Blue)
	•	Channel removal options (remove Blue channel, etc.)
	•	True bypass toggles for each section
	•	Simple, intuitive UI for accessibility

⸻

Intended Use

FadedBalancerOFX is intended for archivists, restoration specialists, and anyone working with digitally scanned film that has experienced dye fading or channel imbalance.
It does not “restore” lost color information but provides flexible controls to make faded footage visually closer to neutral or more pleasant for review, restoration, or access workflows.

⸻

Installation
	1.	Download FadedBalancerOFX.dctl.
	2.	Place it in your DaVinci Resolve LUTs or DCTL folder:
	•	Windows:
C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\
	•	macOS:
/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/
	3.	Restart DaVinci Resolve if it’s open.
	4.	Add the DCTL OFX node in the Color page and select FadedBalancerOFX.

⸻

Usage
	•	Adjust Lift, Gamma, Gain, and Offset for each channel as needed.
	•	Use channel copy toggles to transfer channel data (e.g., copy Red to Blue for faded cyan films).
	•	Use channel removal to zero out an unwanted channel for analytic or creative purposes.
	•	All adjustments are real-time and non-destructive.

⸻

Limitations
	•	This tool cannot restore lost color data; it adjusts existing data for visual improvement.
	•	macOS and Linux are not fully tested in v1.0.0.
	•	Not intended for use outside of DaVinci Resolve.

⸻

License

MIT License

⸻

Credits

Developed by Fabio Bedoya.
