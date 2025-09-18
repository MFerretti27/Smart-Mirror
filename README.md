# General Information
- A Smart Mirror is dislpay current weather and a daily motivational quote.
- Integrated Facial Reconition to detect users that stand in front of the mirror to welcome them by name and tell them a joke.


## Screen Shots



## Controls
Escape - Quit running code or exit adding a new user if in the middle of that proccess.<br />
Return/Enter - Add a new user to recognized.<br />


## Proccess of Adding a New User
- Step 1: Press Return/Enter to start the proccess of adding a new user.<br />
- Step 2: Type the name of the persons face you want to recognize.<br />
- Step 3: Press Enter when finished when done entering new persons name.<br />
- Step 4: Press Enter again to start taking pictures (stand ~3 feet away a move head around to get different angles, will take ~20 seconds.<br />
- Step 5: Choose if the mirror should display nice jokes or mean jokes when it detects a recognized user in front of the mirror (by pressing 1 or 2).<br />
  - If nice is choosen then it will display dad jokes
  - If mean is choosen it will ask specifily what type of mean jokes (racist jokes, sexist jokes, dad jokes, dark humor, my_quotes).<br />

## Requirements
- Python needs to be installed and in your PATH (install [HERE](https://www.python.org/downloads/))<br />
- pip (usually installed with python) needs to be installed <br />
- All other requirements are in requirements.txt file.
  - Run ```pip install -r Requirements.txt``` to install

## Hardware Recommended
- Raspberry PI (version 4 and up)
    - [Link](https://www.amazon.com/Raspberry-Pi-Quad-core-Cortex-A76-Processor/dp/B0CTQ3BQLS/ref=sxin_16_pa_sp_search_thematic_sspa?content-id=amzn1.sym.76d54fcc-2362-404d-ab9b-b0653e2b2239%3Aamzn1.sym.76d54fcc-2362-404d-ab9b-b0653e2b2239&crid=2W4WOFMA7GQFC&cv_ct_cx=raspberry%2Bpi%2B5&dib=eyJ2IjoiMSJ9.9Y9spcqJNnOBeHLQWNTS41xuiL-91jGxokGdWfYaXkN26OVp-gUsmv2kqlxliXXA.-RF009atOtVOBvjkGi-tAig15vDCYjL13yHoA8iGsX0&dib_tag=se&keywords=raspberry%2Bpi%2B5&pd_rd_i=B0CTQ3BQLS&pd_rd_r=a22d1f2f-599f-4cb8-8e5d-9832619347b6&pd_rd_w=go2DS&pd_rd_wg=aZn7Y&pf_rd_p=76d54fcc-2362-404d-ab9b-b0653e2b2239&pf_rd_r=FEB2SVV839B11Z6QKJBH&qid=1731383117&s=electronics&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D&sprefix=ras%2Celectronics%2C190&sr=1-1-6024b2a3-78e4-4fed-8fed-e1613be3bcce-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9zZWFyY2hfdGhlbWF0aWM&th=1)<br />
- Monitor 
    - 22 inch flat monitor [Link](https://www.amazon.com/dp/B0D17P8N28?ref=ppx_yo2ov_dt_b_fed_asin_title)<br />
    - 24 inch Asus monitor [Link](https://www.amazon.com/ASUS-VA24DQ-Adaptive-Sync-DisplayPort-Frameless/dp/B08C5MGFXQ/ref=sr_1_3?crid=3S3T4WEGS9F80&dib=eyJ2IjoiMSJ9.rmF77kGZWbFRIylLifYcthss5lyAUm4EJ3MCJ40pqPqk6E_p4qgSiCnLo3AtyHk0jlxasr3d1r7SRelS4QjWUlJ8WoVcpdJ8JIkxzzURDpKruZxWRjl2bgEddP3chNo-kYixRihIxsh7RNkkfIIuqltU9GVN0nA6SqcF4MWjIJIWxBeebZn1awc6QkvL0lgoY7ORZlWmoiBAFy58rvyO2zj6JnsciaG1HeKXFcKam3c.L37ENfD17MKaFgnxtCRUxVbtX79lT4SiDcT7y2hxc2w&dib_tag=se&keywords=asus+monitor&qid=1748050481&sprefix=asus+monitor%2Caps%2C202&sr=8-3&ufe=app_do%3Aamzn1.fos.9fe8cbfa-bf43-43d1-a707-3f4e65a4b666)
    - 15 inch monitor [Link](https://www.amazon.com/Portable-Ultra-Slim-External-Kickstand-Extender/dp/B0D8JXY8V3/ref=sr_1_1_sspa?crid=IXV836AAVTQY&dib=eyJ2IjoiMSJ9.JFwG8BAM9jkKSm3OAh4xtDYnh0VGDF3iuVvD2ln-HAvVOuW69xYNAH5kzbNq8sVzDK1D9IY5ceWZ-C0EX6IEkSRt8KxpAunjMeQ1XkfiD_zJF_Op2FScahvVyb7t43xlh5HS9T_ujfUZL-NmmMDqGHYFOEsPuZlkTO3SXRK3W1-kjzRWKU3O9FPoVypirbHmYjc_UcHbGqa0_bxOFUF_a1SV5TlbSs0jRIMzGs7JeL0.jqQ152DrfcMx0DyA7sv6mx2l9on_qiKtzkIPrQmWwRQ&dib_tag=se&keywords=ailrinni%2Bportable%2Bmonitor%2B-%2B15.6%2Binch%2Bfull%2Bhd%2B1080p%2Bips&qid=1748048739&sprefix=%2Caps%2C188&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1)<br />
- Remote (Used for setting up a new user - see controls section)
  - [Link](https://www.amazon.com/dp/B06XHF7DNQ?ref=ppx_yo2ov_dt_b_fed_asin_title)
- Camera
- Frame
- 1 way mirror film 
    
