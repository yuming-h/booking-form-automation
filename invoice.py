import os
from pylatex import Document, PageStyle, Head, Foot, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat, StandAloneGraphic, MiniPage, Command
from pylatex.utils import italic, bold, NoEscape

import datetime


def getInvNum():
    dir = os.path.join(os.path.dirname(__file__), 'Invoices/nums.txt')
    inv_log = open(dir, "r+")
    ret = 0
    for line in inv_log:
        if (line != ''):
            ret = int(line)
    ret = ret + 1
    inv_log.write(str(ret) + "\n")
    return ret

def getBookingSpaces(areas):
    ret = ''
    for a in areas:
        ret = ret + a + ', '
    return ret[:-2]

def unit_cost(booking_type, areas):
    if booking_type in 'SUS Groups (Committees)':
        if 'Main Floor (2F)' in areas:
            return 0
        elif 'Mezzanine (3F)' in areas:
            return 0
        elif 'Front Porch' in areas:
            return 0
        else:
             return 0
    if booking_type in 'Science Departmental/Non-Departmental Club':
        if 'Main Floor (2F)' in areas:
            return 0
        elif 'Mezzanine (3F)' in areas:
            return 0
        elif 'Front Porch' in areas:
            return 0
        else:
            return 0
    if booking_type in 'Internal Organization (UBC - Science-Affiliated)':
        if 'Main Floor (2F)' in areas:
            return 0
        elif 'Mezzanine (3F)' in areas:
            return 0
        elif 'Front Porch' in areas:
            return 0
        else:
            return 0
    if booking_type in 'Internal Organization (UBC - Non-Science Affiliated)':
        if 'Main Floor (2F)' in areas:
            return 30
        elif 'Mezzanine (3F)' in areas:
            return 20
        elif 'Front Porch' in areas:
            return 15
        else:
            return 0
    else:
        if 'Main Floor (2F)' in areas:
            return 70
        elif 'Mezzanine (3F)' in areas:
            return 40
        elif 'Front Porch' in areas:
            return 40
        else:
            return 0

def quantity(start, finish):
    fin = finish.hour + (finish.minute / 60 )
    sta = start.hour + (start.minute / 60)
    return round(abs(fin - sta), 2)

def calculate_cost(areas, unit_cost, quantity):
    if "Front Porch" in areas:
        return unit_cost
    else:
        return unit_cost * quantity

def av_cost(booking_type):
    if booking_type in 'SUS Groups (Committees)':
        return 0
    if booking_type in 'Science Departmental/Non-Departmental Club':
        return 0
    if booking_type in 'Internal Organization (UBC - Science-Affiliated)':
        return 0
    if booking_type in 'Internal Organization (UBC - Non-Science Affiliated)':
        return 20
    else:
        return 25

def spkr_cost(booking_type):
    if booking_type in 'SUS Groups (Committees)':
        return 0
    if booking_type in 'Science Departmental/Non-Departmental Club':
        return 20
    if booking_type in 'Internal Organization (UBC - Science-Affiliated)':
        return 30
    if booking_type in 'Internal Organization (UBC - Non-Science Affiliated)':
        return 30
    else:
        return 30
        
# Assume the event is being charged extra hours
def extra_hours(end_datetime):
    if end_datetime.hour > 23:
        calc = (end_datetime.hour + (end_datetime.minute / 60)) - 23
    else:
        calc = (end_datetime.hour + (end_datetime.minute / 60)) + 1
    return round(calc, 2)

def wknd_hours(start_datetime, end_datetime):
    if start_datetime.weekday() > 4:
        return quantity(start_datetime, end_datetime)
    else:
        return round(end_datetime.hour + (end_datetime.minute / 60), 2)

def dep_cost(booking_type, sol):
    if (booking_type == 'SUS Groups (Committees)'):
        return 0
    elif sol:
        return 200
    else:
        return 100

def get_av(equip):
    ret = ''
    for a in equip:
        ret = ret + a + ', '
    return ret[:-2]


def generateInvoice(booking):
    image_filename = os.path.join(os.path.dirname(__file__), 'Invoices/sus_header.png')
    geometry_options = {"tmargin": "1cm", "lmargin": "1.5cm", "rmargin": "1.5cm"}
    doc = Document(geometry_options=geometry_options)
    inv_number = getInvNum()
    now = datetime.datetime.now()
    event_date = booking['date']


    doc.append(Command('noindent'))
    with doc.create(Figure(position='h!')) as sus_pic:
        doc.append(Command('centering'))
        sus_pic.add_image(image_filename, width='500px')
    doc.append(Command('begin', 'center'))
    doc.append(Command('textbf', 'Abdul Ladha Science Student Centre Invoice No. '+str(inv_number)))
    doc.append(Command('end', 'center'))
    doc.append(Command('textbf', ' '))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Date issued: '))
    doc.append(str(now.month)+'-'+str(now.day)+'-'+str(now.year))
    doc.append(Command('newline'))
    doc.append(Command('textbf','Purpose: '))
    doc.append(booking['eventname'] + " on " +
        booking['date'])
    doc.append(Command('newline'))
    doc.append(Command('textbf','Bill to: '))
    doc.append(booking['name'] + ', '+ booking['org'])
    doc.append(Command('newline'))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Booking Fees: ' + booking['type']))
    doc.append(Command('newline'))
    with doc.create(Tabular('|r|ccl|')) as table:
        areas = getBookingSpaces(booking['floors'])
        uc = unit_cost(booking['type'], booking['floors'])
        qn = quantity(booking['daterange'][0], booking['daterange'][1])
        booking_cost = calculate_cost(areas, uc, qn)
        av = av_cost(booking['type'])
        spkr = spkr_cost(booking['type'])
        num_extra_hours = extra_hours(booking['daterange'][1])
        weekend_hours = wknd_hours(booking['daterange'][0], booking['daterange'][1])
        cost = 0


        table.add_hline()
        table.add_row(("Description", "Unit Price", "Quantity", "Amount"))
        table.add_hline()
        table.add_row(areas, uc, qn, booking_cost)
        table.add_hline()
        cost = cost + booking_cost
        if 'Audio System' in booking['audio']:
            table.add_row('Audio System', av, 1, av)
            table.add_hline()
            cost = cost + av
        if '550W Speakers' in booking['audio']:
            table.add_row('550W Speakers', spkr, 1, spkr)
            table.add_hline()
            cost = cost + spkr
        if booking['daterange'][1].hour > 23 or booking['daterange'][1].hour < 5:
            table.add_row('After 11PM Fees', 25, num_extra_hours, 25 * num_extra_hours)
            table.add_hline()
            cost = cost + 25 * num_extra_hours
        if booking['daterange'][1].weekday() > 4:
            table.add_row('Weekend Fees', 35, weekend_hours, 35 * weekend_hours)
            table.add_hline()
            cost = cost + 35 * weekend_hours
        table.add_row('','','Balance Due:', '$'+str(cost))
        table.add_hline()

    doc.append(Command('newline'))
    doc.append(Command('newline'))
    doc.append("Note: The Balance Due above is exclusive of the Deposit. \
    The Deposit (paid separate by cheque or AMS Journal Voucher) must be received by the Building Manager \
    at least two weeks prior to the event, unless stated otherwise by the Building Manager. \
    This Deposit includes, but is not limited to cancellation, damages, cleaning, and other penalty charges. \
    The Deposit is refunded only when ALL conditions are met.")

    doc.append(Command('newline'))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Deposit'))
    doc.append(Command('newline'))
    with doc.create(Tabular('|r|c|c|')) as table:
        deposit_cost = dep_cost(booking['type'], booking['alc'])

        table.add_hline()
        table.add_row(('Item', 'Amount', 'Due Date'))
        table.add_hline()
        table.add_row('Damage Deposit', deposit_cost, '2 weeks prior to the event')
        table.add_hline()

    doc.append(Command('newline'))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'To pay the deposit, please take a picture of a cheque or Journal Voucher made out to \
        Science Undergraduate Society of UBC and email it to the Building Manager along with all the other forms. \
        It will only be deposited if damages are done or if cleanup is done improperly.'))

    doc.append(Command('newline'))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Alma Mater Society (AMS) clubs and constituencies \
    can make booking rental payments via Journal Vouchers; payable to UBC Science Undergraduate Society \
    (Account Number: 474-5028-06). Payment by cash/cheque is also acceptable for both deposit and rental fees \
    (cheques should be made payable to UBC Science Undergraduate Society).'))

    doc.append(Command('newline'))
    doc.append(Command('newline'))
    doc.append('Please quote the invoice number in all correspondence. \
    Payment is due by the deadlines indicated above, unless stated otherwise by the Building Manager. \
    In the case that the Balance Due is not paid on time, the Deposit will not be returned \
    and will be considered a portion of the payment of the fees. No additional bookings can be made if fees are still outstanding. \
    The BMC reserves the right to cancel future events if outstanding fees are unpaid.')

    doc.append(Command('newline'))
    doc.append(Command('newline'))
    doc.append('CANCELLATIONS:  YOU MUST LET THE BUILDING MANAGER KNOW VIA EMAIL ASAP \
    (AT LEAST 1 WEEK PRIOR TO YOUR EVENT) IF YOU CANCEL YOUR BOOKING. \
    OTHERWISE, 100% OF YOUR BOOKING DEPOSIT WILL BE DEPOSITED. NO EXCEPTIONS.')
    doc.append(Command('newline'))
    doc.append(Command('begin', 'center'))
    doc.append(Command('textbf', 'Thank you for booking Ladha!'))
    doc.append(Command('end', 'center'))

    doc.append(Command('newpage'))

    with doc.create(Figure(position='h!')) as sus_pic:
        doc.append(Command('centering'))
        sus_pic.add_image(image_filename, width='500px')


    doc.append(Command('begin', 'center'))
    doc.append(Command('textbf', 'Abdul Ladha Science Student Centre Booking Summary No. '+str(inv_number)))
    doc.append(Command('end', 'center'))
    doc.append(Command('textbf', ' '))
    doc.append(Command('newline'))

    doc.append(Command('textbf', 'Organizer Information:'))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Oranizer Name: '))
    doc.append(booking['name'])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Organizer Title/Position: '))
    doc.append(booking['title'])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Organization: '))
    doc.append(booking['org'])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Phone Number: '))
    doc.append(booking['phone'])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Email: '))
    doc.append(booking['email'])
    doc.append(Command('newline'))
    doc.append(Command('newline'))

    doc.append(Command('textbf', 'Booking Details: '))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Booking Status: '))
    doc.append('Pending')
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Event Supervisor: '))
    doc.append(booking['sup'][0])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Event: '))
    doc.append(booking['eventname'])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Event Date: '))
    doc.append(booking['date'])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Event Time: '))
    doc.append(booking['starttime'] + ' - ' + booking['endtime'])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Booked Areas: '))
    doc.append(getBookingSpaces(booking['floors']))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'A/V Equipment: '))
    doc.append(booking['audio'])
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Expected Attendance: '))
    doc.append(str(booking['count']))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Number of Staff: '))
    doc.append(str(booking['staff']))
    doc.append(Command('newline'))
    doc.append(Command('newline'))

    doc.append(Command('textbf', 'Special Occasion License (SOL): '))
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'License Required? (y/n): '))
    if booking['alc']:
        doc.append('YES')
    else:
        doc.append('NO')
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Security Required? (y/n): '))
    if booking['alc']:
        doc.append('YES')
    else:
        doc.append('NO')
    doc.append(Command('newline'))
    doc.append(Command('textbf', 'Forms Required: '))
    if booking['alc']:
        doc.append('Permission to Hold a Licensed Event, Faculty of Science Organizer’s Plan, \
        Request for University Permission to Hold a Function where Alcohol will be Served')
    else:
        doc.append('N/A')
    doc.append(Command('newline'))

    doc.generate_pdf('Invoices/Invoice '+str(inv_number), clean_tex=False, compiler='pdflatex')
    return inv_number
