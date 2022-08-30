import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# List of SAAS organizations
sass_list = ['30DC INC', '3D PIONEER SYSTEMS INC', 'ACTUA CORP', 'ADEXA INC', 'ADVANCED VOICE RECOGNITION', 'ADVANT-E CORP', 'ADVANTEGO CORP', 'ALLDIGITAL HOLDINGS INC', 'AMERICAN SECURITY RES CORP', 'AMERICAN SOFTWARE  -CL A', 'APPLIED VISUAL SCIENCES INC', 'APT SYSTEMS INC', 'AVAYA HLDGS CORP', 'BARRACUDA NETWORKS INC', 'BIGCOMMERCE HOLDIN INC', 'BLACK BOX CORP', 'BLAQCLOUDS INC', 'BRAVATEK SOLUTIONS INC', 'BRIDGEWAY NATIONAL CORP', 'B-SCADA INC', 'BUSYBOX.COM INC', 'CERIDIAN CORP', 'CHANGSHENG INTERNATIONAL GRO', 'CHANNELADVISOR CORP', 'CHINA YANYUN YHU NTL ED GRP', 'CICERO INC', 'CIMETRIX INC', 'CIPHERLOC CORP', 'CLICKSTREAM CORP', 'CLONE ALGO TECHNOLOGIES INC', 'CLOUDERA INC', 'CLOUDWARD INC', 'CODE REBEL CORP', 'COM GUARD.COM INC', 'CORNERSTONE ONDEMAND INC', 'CYBERFORT SOFTWARE INC', 'DEALERADVANCE INC', 'DIGILITI MONEY GROUP INC', 'DUCK CREEK TECHNOL INC', 'E2OPEN INC', 'ELASTIC NETWORKS INC', 'ELASTIC NV', 'ELCOM INTERNATIONAL INC', 'ENTERPRISE INFORMATICS INC', 'EZENIA INC', 'FALCONSTOR SOFTWARE INC', 'FANTASY ACES DAILY FANTASY', 'FIREEYE INC', 'FLEXSHARES IBOXX 3-YR TAR FD', 'FLEXSHARES IBOXX 5-YR TAR FD', 'FRIENDFINDER NETWORKS INC', 'GIVEMEPOWER CORP', 'GRANDPARENTS.COM INC', 'GREEN POLKADOT BOX INC', 'HOPTO INC', 'HRSOFT INC', 'IBSG INTERNATIONAL INC', 'IMAGEWARE SYSTEMS INC', 'INFORMATION RESOURCES INC', 'INTEGRATED BUSINESS SYS &SVC', 'INTELLIGENT SYSTEM CORP', 'INTELLINETICS INC', 'INTERMAP TECHNOLOGIES CORP', 'INTERNATIONAL LEADERS CAP CO', 'IRONCLAD ENCRYPTION CORP', 'ISHARES IBOXX HIGH YLD CP BD', 'ISHARES IBOXX INVST GR CP BD', 'ISIGN SOLUTIONS INC', 'ISOCIALY INC', 'IVEDA SOLUTIONS INC', 'J2 GLOBAL INC', 'JDA SOFTWARE GROUP INC', 'KIWIBOX COM INC', 'KRONOS INC', 'LAWSON SOFTWARE INC', 'LEVELBLOX INC', 'LIQUI-BOX CORP', 'LIQUID HOLDINGS GROUP INC', 'LIVE MICROSYSTEMS INC', 'MAIL BOXES ETC', 'MAX SOUND CORP', 'MEDALLIA INC', 'MEDALLIANCE INC', 'MEDIATECHNICS CORP', 'MGT CAPITAL INVESTMENTS INC', 'MIX TELEMATICS LTD', 'MOBILEIRON INC', 'MONSTER ARTS', 'NEOMEDIA TECHNOLOGIES INC', 'NOTIFY TECHNOLOGY CORP', 'OMTOOL LTD', 'PAID INC', 'PALANTIR TECHNOLOG INC', 'PARETEUM CORP', 'PAYBOX CORP', 'PLURALSIGHT INC', 'PRIMAL SOLUTIONS INC', 'PROOFPOINT INC', 'PULSE EVOLUTION CORP', 'QAD INC', 'QUANTGATE SYSTEMS INC', 'RAADR INC', 'RAND WORLDWIDE INC', 'REALPAGE INC', 'RIGHTSCORP INC', 'ROCKETFUEL BLOCKCHAIN INC', 'RORINE INTL HOLDING CORP', 'ROSETTA STONE INC', 'SAILPOINT TECHNO HLDG', 'SCIENT INC', 'SHARPSPRING INC', 'SIMTROL INC', 'SITO MOBILE LTD', 'SKYBOX INTL INC', 'SLACK TECHNOLOGIES INC', 'SMARTMETRIC INC', 'SOFTECH INC', 'SS&C TECHNOLOGIES HLDGS INC', 'SSI INVESTMENTS II LTD', 'SVMK INC', 'SYNACOR INC', 'TAUTACHROME INC', 'TELENAV INC', 'THEGLOBE.COM INC', 'TIBCO SOFTWARE INC', 'TINTRI INC', 'TMM INC', 'ULTIMATE SOFTWARE GROUP INC', 'UNITRONIX CORP', 'VANCORD CAPITAL INC', 'VDO-PH INTERNATIONAL INC', 'VERB TECHNOLOGY CO INC', 'VERTICAL COMPUTER SYS INC', 'VIVA ENTERTAINMENT GROUP INC', 'VMWARE INC -CL A', 'VOYAGER DIGITAL LTD', 'VUBOTICS INC', 'WOD RETAIL SOLUTIONS', 'XCELMOBILITY INC', 'YAPPN CORP', 'ZOOM TELEPHONICS INC', 'ZOOM VIDEO COMUNICATIONS INC', 'ZOOMAWAY TRAVEL INC']

# Path to Chrome driver for Selenium's operations
PATH = r'path_to_chrome_web_driver'
# CIK query base url
URL = "https://sec.report/CIK/Search/SEARCH"
OUTPUT_DIR = 'result' # storage directory for the output

driver = webdriver.Chrome(PATH)
driver.get(URL)
time.sleep(0.5)

n=0
data = []
fail = []
f = open("log1.txt", "x") # logging

for firm in sass_list:
    try:
        main = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.ID,"company"))
        ) 
    except:
        driver.quit()
    field = driver.find_element_by_id('company')
    field.send_keys(firm)
    field.send_keys(Keys.RETURN)
    try:
        main = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.ID,"company"))
        ) 
    except:
        driver.quit()

    links= driver.find_elements_by_tag_name('tr')
    for fr in links:
        found = False
        skip = False
        cols = fr.find_elements_by_tag_name('td')
        for i in cols:
            if i.text != '':
                if cols[0].text =='No Matching Companies, Please Retry Your Search.':
                    skip = True
                    break
                found = True
                f.write(firm + " -> " + cols[0].text + " " + cols[1].text+"\n")
                xyz = {
                    'name':firm,
                    'cik':cols[1].text
                }
                data.append(xyz)
                n+=1
                break
        
        if found or skip:
            break

    if not found or skip:
        fail.append(firm)
    
print(fail)
print(n)
print(len(fail))
driver.quit()

df = pd.DataFrame.from_dict(data)
df.to_csv("{}/res2.csv".format(OUTPUT_DIR)) # Stores the CIK for each organization
f.close()