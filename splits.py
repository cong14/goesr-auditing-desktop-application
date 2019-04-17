from collections import OrderedDict

physical_location = ["G-NSOF-N-3008-NSOMM03_B04", "G-HONEYWELL", "G-NSOF-N-3008-NSIMM01-A31",
                     "G-WCDAS-W-101-WSOMM02-A32", "A-RBU-R-HR9-RBU3_SSPA S-BAND CAB1-A13C_16MRFU",
                     "A-WCDAS-W-HR6-WCDAS3_SSPA S-BAND CAB2_16MRFU_A31A", "A-GDST",
                     "A-RBU-R-HR7-RBU1_SSPA S-BAND CAB2_16MRFU_A13A","A-WCDAS-W-GOES WEST ROOM-RK_WCDAS1_5AZ2_A9"]

i = 1
phys_loc_fields = ['system', 'site', 'room', 'rack']
for location in physical_location:
    print ("***** LOCATION #{} *****".format(i))
    try:
        loc_parts = location.split('-',4)
        if len(loc_parts) > 2:
            loc_parts[2:4] = ['-'.join(loc_parts[2:4])]

        phys_loc_dict = {}

        for j in range(len(phys_loc_fields)):
            try:
                phys_loc_dict[phys_loc_fields[j]] = loc_parts[j]
            except IndexError:
                phys_loc_dict[phys_loc_fields[j]] = 'NULL'
            j += 1

        print loc_parts
    except Exception as e:
        print e
    i += 1

    print phys_loc_dict