from fpdf import FPDF
from datetime import datetime
import shutil
import pandas as pd
import csv
import os

baseDir = os.path.join(os.getcwd(), "assets")
file_to_be_parsed = os.path.join(os.getcwd(), "uploads/grades.csv")
subNameMapping = os.path.join(os.getcwd(), "uploads/subjects_master.csv")
studNameMapping = os.path.join(os.getcwd(), "uploads/names-roll.csv")

masterList = []
studNameMap = {}
dfl = {}
dct = {}

branchMap = {
    "CS": "Computer Science and Engineering",
    "CB": "Chemical Engineering",
    "EE": "Electrical & Electronics Engineering",
    "ME": "Mechanical Engineering",
    "MM": "Metallurgical Engineering",
    "CE": "Civil Engineering",
    "CH": "Chemistry",
}

gradeMap = {
    "AA": 10,
    "AB": 9,
    "BB": 8,
    "BC": 7,
    "CC": 6,
    "CD": 5,
    "DD": 4,
    "F": 0,
    "I": 0,
}


def prepLists():
    for ind, line in enumerate(csv.reader(open(studNameMapping))):
        if ind > 0:
            studNameMap[line[0]] = line[1]

def fixWildcardEntry(grade) -> str:
    return grade.replace("*", "") if grade[len(grade) - 1] == "*" else grade


def prepOverallResult(rollNum: str):
    spi, cpi = ["SPI"], ["CPI"]

    masterList = []
    for ind, line in enumerate(csv.reader(open(file_to_be_parsed))):
        masterList.append(line)

    maxSem = 0

    # Find max sems for a roll no
    for ind, line in enumerate(masterList):
        if line[0] == rollNum:
            maxSem = max(maxSem, int(line[1]))
    maxSem += 1  # As range iterates till maxValue - 1

    semwiseCreds = ["Semester wise Credit Taken"]
    fullCreds = ["Total Credits Taken"]
    clearedCreds = ["Total Credits Cleared"]
    semRow = ["Semester No", 1]

    for f in range(1, maxSem):
        ms, cls, spis = 0, 0, 0
        for ind, line in enumerate(masterList):
            if ind > 0:
                if line[0] == rollNum:  # Fix a roll no
                    if int(line[1]) == f:  # Iterate on a specific sem
                        ms += int(line[3])
                        finalGrade = fixWildcardEntry(line[4].strip())
                        if finalGrade == "F" or finalGrade == "I":
                            pass
                        else:
                            cls += int(line[3])
                        spis += int(line[3]) * gradeMap[finalGrade]

        # Handle the case for the sem which does not exist
        mSemWiseClsCreds = cls
        mSpi = 0
        mSemWiseCreds = 0
        if ms > 0:
            mSpi = (spis / ms).__round__(2)
            mSemWiseCreds = ms
        spi.append(mSpi)
        semwiseCreds.append(mSemWiseCreds)
        clearedCreds.append(mSemWiseClsCreds)

    mCpi = spi[1] * semwiseCreds[1]
    dynCreds = semwiseCreds[1]
    fullCreds.append(dynCreds)
    cpi.append(spi[1])  # Because CPI in 1st sem is same as SPI in 1st sem

    for sem in range(2, maxSem):
        semRow.append(sem)
        dynCreds += semwiseCreds[sem]
        fullCreds.append(dynCreds)
        mCpi += spi[sem] * semwiseCreds[sem]
        cpi.append((mCpi / dynCreds).__round__(2))

    return maxSem - 1, semwiseCreds, clearedCreds, spi, cpi

def checkForImg(imgName) -> bool:
    conts = os.listdir(os.path.join(os.getcwd(), "uploads"))
    if imgName not in conts:
        return False
    return True

def prepPdfForRolls(rng: []):
    sealAv = checkForImg("seal.jpeg")
    signAv = checkForImg("sign.jpeg")
    for roll in rng:
        dims = {}
        stdims = {}
        txtForSem = {}
        missed = 0
        if roll in dfl:
            sems, swcreds, clsCreds, spiz, cpiz = prepOverallResult(roll)
            pdf = FPDF(orientation="L", unit="mm", format="A3")
            pdf.add_page()
            pdf.set_font("Times", size=8.5)
            line_height = pdf.font_size * 1.5
            pdf.rect(x=10, y=10, w=pdf.w - 20, h=pdf.h-20, style="")
            pdf.rect(x=85, y=43, w=(pdf.w / 2) + 20, h=15, style="")
            fmtr = 0
            pdf.image(os.path.join(os.getcwd(), "assets/tsBanner.png"), x=10, y=10, w=pdf.w - 20)
            prg = ""
            temp = roll
            if str(temp)[2] == '1':
                prg = "Master of Technology"
            if str(temp)[2] == '2':
                prg = "PhD"
            if str(temp)[2] == '0':
                prg = "Bachelor of Technology"
            pdf.set_font(size=12, style="B")
            pdf.text(x=87, y=48, txt=f"Roll No:  {roll}                                     Name: {studNameMap[roll]}                                            Year of Admission:  20{roll[0] + roll[1]}")
            pdf.text(x=87, y=55, txt=f"Programme: {prg}       Course: {branchMap[str(temp[4] + temp[5])]}")

            pdf.set_font(size=10, style="")
            abscissa = 7
            ordinate = 64
            recy = 0
            recx = 0
            tx = 7
            pdf.set_y(ordinate+5)

            for sem in range(sems):
                indx = 0
                if (sem) % 4 == 0 and sem > 0:
                    pdf.set_x(recx)
                if sem + 1 in dfl[roll].keys():
                    for info in dfl[roll][sem + 1]:
                        if abscissa != 0:
                            pdf.set_x(abscissa + 8)
                            rind = 0
                        wdh = 0
                        ls = len(info) + 1
                        for ir in range(ls):
                            if rind == 0: 
                                wdh = 14
                            elif rind == 1:
                                wdh = 75
                            elif rind == 2:
                                wdh = 13
                            elif rind == 4 or rind == 3:
                                wdh = 11

                            if indx == 0:
                                pdf.set_font(style="B")
                            else:
                                pdf.set_font(style="")
                            if ir < ls - 1:
                                if sem not in stdims:
                                    stdims[sem] = []
                                    stdims[sem] = [pdf.get_x(), pdf.get_y()]
                                    pdf.set_font(style="BU", size=10)
                                    pdf.text(x=stdims[sem][0], y=stdims[sem][1] - 1, txt=f"Semester {sem + 1}")
                                    pdf.set_font(style="")
                                    pdf.set_xy(x=stdims[sem][0], y=stdims[sem][1])
                                pdf.multi_cell(wdh, line_height, str(info[ir]), border=1, ln=3, max_line_height=pdf.font_size, align="C")
                            rind += 1
                        if indx == (len(dfl[roll][sem + 1]) - 1):
                            if sem not in dims:
                                dims[sem] = []
                            dims[sem] = [pdf.get_x().__round__(2), pdf.get_y().__round__(2)]
                            abscissa = pdf.get_x()
                            tx = pdf.get_x()
                            if (sem + 1) % 3 == 0:
                                recy = pdf.get_y() + 22.5
                                abscissa = 7
                                recx = abscissa
                            cx, cy = pdf.get_x() - 110, pdf.get_y() + 8
                            pdf.set_font(style="B", size=10)
                            pdf.text(x=cx - 12, y= cy + 2, txt=f"Total Credits: {str(swcreds[sem + 1])}  Credits cleared: {str(clsCreds[sem + 1])}    SPI: {str(spiz[sem + 1])}   CPI: {str(cpiz[sem + 1])}")
                            pdf.rect(x=cx - 14, y=cy - 2, w=94, h=5.6, style="")
                            pdf.set_font(style="", size=9)
                            ah = recy if recy > 0 else ordinate
                            pdf.set_y(ah)
                            ordinate = pdf.get_y()
                        indx += 1
                        pdf.ln(line_height)
                else:
                    missed += 1
                    continue
            ldims = len(dims) - missed - 1
            if signAv:
                pdf.image(os.path.join(os.getcwd(), "uploads/sign.jpeg"), x=pdf.w-65, y=dims[ldims][1] + 37, w=40)
            if sealAv:
                pdf.image(os.path.join(os.getcwd(), "uploads/seal.jpeg"), x=(pdf.w - 20)/2, y=dims[ldims][1] + 27, w=40)
            pdf.line(x1=10, y1=dims[ldims][1] + 30, x2= pdf.w - 10, y2=dims[ldims][1] + 28)

            xco = dims[ldims][0] + 80
            yco = dims[ldims][1] + 50
            pdf.line(xco, yco, xco + 50, yco)
            pdf.set_font(size=14, style="B")
            pdf.text(xco - 42, yco, txt="Assitant Registrar")
            pdf.text(20, yco, txt=f"Date Generated: {datetime.today().strftime('%d-%m-%Y | %H:%M:%S')}")
            pdf.output(f"transcriptsIITP/{roll}.pdf")
        else:
            continue
    return


def prepMs(rnz, all=False):
    temp = rnz.replace(" ", "").split("-")

    validRange = []
    absValidRange = []
    invzRolls = []
    lulz = False

    if not all:
        if len(temp) == 1:
            return False, []

        for f in range(7):
            if temp[1][f] != temp[1][f]:
                lulz = True
                return False, []

        if not lulz:
            start = int(temp[0][-2:])
            end = int(temp[1][-2:]) + 1
        
        for num in range(start, end):
            tempo = f"{num}"
            if len(str(num)) == 1:
                tempo = f"0{num}"
            validRange.append(f"{temp[0][:6]}{tempo}")
    
    if os.path.exists(os.path.join(os.getcwd(), "transcriptsIITP")):
        shutil.rmtree(os.path.join(os.getcwd(), "transcriptsIITP"))
    os.mkdir(os.path.join(os.getcwd(), "transcriptsIITP"))

    prepLists()
    somethingAns = pd.read_csv(file_to_be_parsed)
    dFrame = pd.read_csv(file_to_be_parsed, usecols=[0, 1, 2, 3, 4, 5], index_col=0)
    dFrame.sort_values(by=["Roll", "Sem", "SubCode"], inplace=True)

    cntr = 1

    for index, contents in enumerate(csv.reader(open(subNameMapping))):
        if index > 1:
            for ind in contents:
                dct[contents[0]] = [contents[1], contents[2]]

    for index, line in dFrame.iterrows():
        if index not in dfl:
            dfl[index] = {}
        if line[0] not in dfl[index]:
            dfl[index][line[0]] = []
            dfl[index][line[0]].append(["Sub", "Course Name", "L-T-P", "CRD", "GRD"])
        dfl[index][line[0]].append(
            [line[1], dct[line[1]][0], dct[line[1]][1], line[2], line[3]]
        )
        if all and (rnz.strip(" ") == ""):
            absValidRange.append(index)

    if not all:
        for sth in validRange:
            if sth in dfl:
                absValidRange.append(sth)
            else:
                invzRolls.append(sth)

    prepPdfForRolls(absValidRange)
    # prepareTranscriptsArchive()
    dfl.clear()
    return True, invzRolls

def prepareTranscriptsArchive():
    if os.path.exists(os.path.join(os.getcwd(), "transcriptsIITP")):
        if len(os.listdir(os.path.join(os.getcwd(), "transcriptsIITP"))) > 0:
            shutil.make_archive("transcripts", "zip", os.path.join(os.getcwd(), "transcriptsIITP"))
            return True
        return False
    else:
        return False

def main():
    #prepMs("1901CS01-1901CS04")
    #print("done")
    pass

if __name__ == "__main__":
    main()
