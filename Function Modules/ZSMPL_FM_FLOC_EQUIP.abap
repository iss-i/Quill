FUNCTION ZSMPL_FM_FLOC_EQUIP.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_ROOM) TYPE  EQUNR
 *"     REFERENCE(IV_EQUI_TYPE) TYPE  EQTYP
 *"     REFERENCE(IV_FLOC_SETUP) TYPE  ABAP_BOOL OPTIONAL
 *"     REFERENCE(IV_PLANT) TYPE  WERKS_D OPTIONAL
 *"     REFERENCE(IV_TPLKZ) TYPE  TPLKZ OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(ET_EQUI_ID) TYPE  /SMPL/STR_TT_EQUI_ID
 *"     REFERENCE(ET_EQUI_DESC) TYPE  /SMPL/STR_TT_EQUI_DESC
 *"     REFERENCE(ET_EQUI_STAT) TYPE  /SMPL/STR_TT_EQUI_STAT
 *"     REFERENCE(ET_EQUI_DATS) TYPE  /SMPL/STR_TT_EQUI_DATS
 *"     REFERENCE(ET_EQUI_PROD) TYPE  /SMPL/STR_TT_EQUI_PROD
 *"     REFERENCE(ET_EQUI_TYPE) TYPE  /SMPL/STR_TT_EQUI_TYPE
 *"     REFERENCE(ET_CALIB_DUE_DATE) TYPE  /SMPL/STR_TT_EQUI_DATS
 *"  EXCEPTIONS
 *"      EQUIPMENT_DOES_NOT_EXIST
 *"      STATUS_NOT_CONFIGURED
 *"      INITIAL_CLEAN_INCOMPLETE
 *"      ROOM_NOT_MAINTAINED
 *"      CLEANING_REQUIRED
 *"----------------------------------------------------------------------
 *{   INSERT         ARSK902148                                        1
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_FLOC_EQUIP                               *
 * Project/Ticket  : SMPL / NA                                         *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : JCRAIG Jason Craig                                 *
 * Functional                                                           *
 *    Analyst:     : <SAP ID> <Full Name>                               *
 * Create Date     : 21.01.2026                                         *
 * Description     : Equipment Assignment ~ Load static equipment       *
 *                   assigned to the functional location via room alias *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *----------------------------------------------------------------------*
 
  TYPES: BEGIN OF lty_equipment,
            equnr TYPE equnr,
            eqktx TYPE ktx01,
            eqfnr TYPE eqfnr,
            eqtyp TYPE eqtyp,
          END OF lty_equipment.
 
  TYPES: BEGIN OF lty_equi_clean_details,
            rntyr_num   TYPE /smpl/elb_equip-entry_num,
            equi_id     TYPE /smpl/elb_equip-equi_id,
            status      TYPE /smpl/elb_equip-status,
            status_date TYPE /smpl/elb_equip-status_date,
            material    TYPE /smpl/elb_equip-material,
            order_num   TYPE /smpl/elb_equip-order_num,      "added for retrieving previous stat entry if entered from CP
            updat_cb    TYPE /smpl/elb_equip-updat_cb,            "added for retrieving previous stat entry if entered from CP
            equi_stat   TYPE /smpl/elb_eqstat-eq_stat,
            manf_ind    TYPE /smpl/elb_eqstat-manf_ind,
          END OF lty_equi_clean_details.
 
  TYPES: BEGIN OF lty_equi_material_details,
            entry_num TYPE /smpl/elb_equip-entry_num,
            equi_id   TYPE /smpl/elb_equip-equi_id,
            status    TYPE /smpl/elb_equip-status,
            material  TYPE /smpl/elb_equip-material,
            order_num TYPE /smpl/elb_equip-order_num,         "added for retrieving previous stat entry if entered from CP
            updat_cb  TYPE /smpl/elb_equip-updat_cb,          "JCRAIG2904 "added for retrieving previous stat entry if entered from CP
          END OF lty_equi_material_details.
 
  TYPES: BEGIN OF lty_equi_date_details,
            entry_num   TYPE /smpl/elb_equip-entry_num,
            equi_id     TYPE /smpl/elb_equip-equi_id,
            status      TYPE /smpl/elb_equip-status,
            status_date TYPE /smpl/elb_equip-status_date,
            order_num   TYPE /smpl/elb_equip-order_num,        "added for retrieving previous stat entry if entered from CP
            updat_cb    TYPE /smpl/elb_equip-updat_cb,              "added for retrieving previous stat entry if entered from CP
          END OF lty_equi_date_details.
 
DATA: lx_equipment             TYPE lty_equipment,
         lt_equipment             TYPE TABLE OF lty_equipment,
         lt_equi_clean_details    TYPE TABLE OF lty_equi_clean_details,
         lx_equi_clean_details    LIKE LINE OF lt_equi_clean_details,
         l_error                  TYPE boolean,
         l_id                     TYPE icon-id,
         l_stat_prod              TYPE maktx,
         l_equipment              TYPE equnr,
         lt_equi_material_details TYPE TABLE OF lty_equi_material_details,
         lx_equi_material_details LIKE LINE OF lt_equi_material_details,
         lt_equi_date_details     TYPE TABLE OF lty_equi_date_details,
         lx_equi_date_details     LIKE LINE OF lt_equi_date_details,
         l_room                   TYPE equnr,
         l_raumnr                 TYPE raumnr,
         lt_clean_stats           TYPE /smpl/str_tt_equi_stat,
         lt_use_stat              TYPE /smpl/str_tt_equi_stat,
         lv_in_use                TYPE /smpl/str_de_equi_stat,
         lv_clean_1               TYPE /smpl/str_de_equi_stat,
         lv_clean_2               TYPE /smpl/str_de_equi_stat,
         lv_clean_3               TYPE /smpl/str_de_equi_stat,
         lt_floc                  TYPE TABLE OF tplnr.
 

  CONSTANTS: cv_date        TYPE dats VALUE '99991231',
              lc_eqlfn       TYPE eqlfn VALUE '001',
              lc_use_class   TYPE char2 VALUE 'U',  " U1>U
              lc_clean_class TYPE char2 VALUE 'C',
              lc_type_p      TYPE char1 VALUE 'P',
              lc_type_c      TYPE char1 VALUE 'C',
              lc_equi_char   TYPE atinn VALUE 0000001199.  "Characteristic no. for ZSMPL_CHAR_CALIB_DUE_DATE_CHAR.
 
  "MOD4 - Initialize local variables
   CLEAR: lx_equipment, lx_equi_clean_details, lx_equi_material_details,
        lx_equi_date_details, l_error,
        l_id, l_stat_prod, l_equipment,
        l_room, l_raumnr, lv_in_use, lv_clean_1,
        lv_clean_2, lv_clean_3.
 
  REFRESH: lt_equipment,
            lt_equi_clean_details,
            lt_equi_material_details,
            lt_equi_date_details,
            lt_clean_stats,
            lt_use_stat.
 
  " Status retrieval
   "Get Clean Statuses
   PERFORM get_eq_stat_by_class USING lc_clean_class abap_true CHANGING lt_clean_stats.
   READ TABLE lt_clean_stats INDEX 1 INTO lv_clean_1.
   IF sy-subrc <> 0.
     RAISE status_not_configured.
   ENDIF.
 
  READ TABLE lt_clean_stats INDEX 2 INTO lv_clean_2.
   IF sy-subrc <> 0.
     RAISE status_not_configured.
   ENDIF.
 
  READ TABLE lt_clean_stats INDEX 3 INTO lv_clean_3.
   IF sy-subrc <> 0.
     lv_clean_3 = lv_clean_2.
   ENDIF.
 
  " Get IN USE status
   PERFORM get_eq_stat_by_class USING lc_use_class abap_true CHANGING lt_use_stat.
   READ TABLE lt_use_stat INDEX 1 INTO lv_in_use.
   IF sy-subrc <> 0.
     RAISE status_not_configured.
   ENDIF.
 

  "Remove leading zeros from room number
   l_room = iv_room.
 
  "Add leading zeros for filter
   CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
     EXPORTING
       input  = l_room
     IMPORTING
       output = l_room.
 
  "Get Room number from SAP Equipment ID to locate static equipment
   SELECT SINGLE iloa~msgrp
     INTO @l_raumnr
     FROM iloa INNER JOIN equz ON equz~iloan = iloa~iloan
     WHERE equz~equnr = @l_room.
 
  IF sy-subrc NE 0 OR l_raumnr IS INITIAL.
     "use l_room/iv_room
   ELSE.
     l_room = l_raumnr.
   ENDIF.
 
  IF l_room IS INITIAL.
     RAISE room_not_maintained.
   ENDIF.
 
  CALL FUNCTION 'CONVERSION_EXIT_ALPHA_OUTPUT'
     EXPORTING
       input  = l_room
     IMPORTING
       output = l_room.
 
  "Add Functional Location logic to select equipment from FLOC, based on the provided Room
   IF iv_floc_setup = abap_true.
 
    DATA(lv_room_norm) = l_room.
 
      SELECT equi~equnr, eqkt~eqktx, ieq~eqfnr, equi~eqtyp
        FROM equi
        INNER JOIN equz ON equi~equnr = equz~equnr
        INNER JOIN iloa AS ieq ON equz~iloan = ieq~iloan
        INNER JOIN iflot ON ieq~tplnr = iflot~tplnr
        INNER JOIN iloa AS ifl ON iflot~iloan = ifl~iloan
        LEFT  JOIN eqkt ON equi~equnr = eqkt~equnr AND eqkt~spras = @sy-langu
        WHERE iflot~iwerk = @iv_plant
          AND iflot~tplnr <> ''
          AND ( iflot~tplkz = @iv_tplkz OR @iv_tplkz IS NULL )
          AND ifl~msgrp = @l_room
          AND equz~datbi = @cv_date
          AND equz~eqlfn = @lc_eqlfn
          AND equi~eqtyp = @iv_equi_type
        INTO TABLE @lt_equipment.
 
  ELSE.
     "Get the room details to allow for room assignment
     SELECT equi~equnr, eqkt~eqktx, iloa~eqfnr, equi~eqtyp
       FROM equi
       LEFT OUTER JOIN equz ON equi~equnr = equz~equnr
       LEFT OUTER JOIN iloa ON equz~iloan = iloa~iloan
       LEFT OUTER JOIN crhd ON iloa~ppsid = crhd~objid
       LEFT OUTER JOIN eqkt ON equi~equnr = eqkt~equnr AND eqkt~spras = @sy-langu
       INTO @lx_equipment
       WHERE iloa~msgrp = @l_room
       AND equz~datbi = @cv_date
       AND equz~eqlfn = @lc_eqlfn
       AND equi~eqtyp <> @iv_equi_type.
       APPEND lx_equipment TO lt_equipment.
     ENDSELECT.
 
  ENDIF.
 
  "Return error if no equipment exists
   IF sy-subrc NE 0 AND lx_equipment IS INITIAL.
     MESSAGE TEXT-023 TYPE 'S' DISPLAY LIKE 'E'.
     RAISE equipment_does_not_exist.
   ENDIF.
 
  SORT lt_equipment BY equnr.
 
  LOOP AT lt_equipment INTO lx_equipment.
 
    l_equipment = lx_equipment-equnr.
 
    CALL FUNCTION 'CONVERSION_EXIT_ALPHA_OUTPUT'
       EXPORTING
         input  = l_equipment
       IMPORTING
         output = l_equipment.
 
    "Check if equipment has been cleaned in the last 30days
 
    "If equipment has not been cleaned recently, inform operator
     IF l_error EQ lc_type_c.
 
      "Individual equipment do not require 30-day clean warning, as individual status will display
       " TO_BE_CLEANED - Room & Additional Equipment will trigger deviation only
 
    ELSEIF l_error EQ lc_type_p.
 
      " Individual equipment do not require 30-day clean warning, as individual status will display
       " TO_BE_CLEANED - Room & Additional Equipment will trigger deviation only
 
    ENDIF.
 
    "Get number of rows in current logbook
     SELECT /smpl/elb_equip~entry_num, /smpl/elb_equip~equi_id, /smpl/elb_equip~status, /smpl/elb_equip~status_date, /smpl/elb_equip~material,
            /smpl/elb_equip~order_num, /smpl/elb_equip~updat_cb   "JCRAIG2904
       FROM /smpl/elb_equip
       WHERE /smpl/elb_equip~equi_id = @lx_equipment-equnr
       ORDER BY entry_num DESCENDING
     INTO TABLE @lt_equi_clean_details.
 
    IF sy-subrc <> 0.
       MESSAGE TEXT-005 && ` ` && '-' && ` ` && |{ lx_equipment-equnr ALPHA = OUT }| TYPE 'S' DISPLAY LIKE 'E'.
       RAISE initial_clean_incomplete.
     ENDIF.
 
    "Get last product used in current logbook
     SELECT /smpl/elb_equip~entry_num, /smpl/elb_equip~equi_id, /smpl/elb_equip~status, /smpl/elb_equip~material,
            /smpl/elb_equip~order_num, /smpl/elb_equip~updat_cb    "JCRAIG2904
       FROM /smpl/elb_equip
       FOR ALL ENTRIES IN @lt_use_stat
       WHERE /smpl/elb_equip~equi_id = @lx_equipment-equnr
       AND /smpl/elb_equip~status = @lt_use_stat-table_line
 *      ORDER BY entry_num DESCENDING
     INTO TABLE @lt_equi_material_details.
 
    SORT lt_equi_material_details BY entry_num DESCENDING.
 
    IF sy-subrc <> 0.
       "Proceed with initial values for equipment's first clean/use
     ENDIF.
 
    "Get last clean date in current logbook
     SELECT /smpl/elb_equip~entry_num, /smpl/elb_equip~equi_id, /smpl/elb_equip~status, /smpl/elb_equip~status_date,
            /smpl/elb_equip~order_num, /smpl/elb_equip~updat_cb   "JCRAIG2904
       FROM /smpl/elb_equip
       WHERE /smpl/elb_equip~equi_id = @lx_equipment-equnr
       AND ( /smpl/elb_equip~status = @lv_clean_1 OR /smpl/elb_equip~status = @lv_clean_2 OR /smpl/elb_equip~status = @lv_clean_3 )  "MOD1
       ORDER BY entry_num DESCENDING
     INTO TABLE @lt_equi_date_details.
 
    IF sy-subrc <> 0.
       "Proceed with initial values for equipment's first clean/use
     ENDIF.
 
    "Read number of table rows
     READ TABLE lt_equi_clean_details INTO lx_equi_clean_details INDEX 1.
     "JCRAIG2904
     IF lx_equi_clean_details-updat_cb = ''.
       READ TABLE lt_equi_clean_details INTO lx_equi_clean_details INDEX 2.
       IF sy-subrc <> 0.
         "zero entries are handled by related SELECT
         MESSAGE TEXT-015 TYPE 'S' DISPLAY LIKE 'E'.
         RAISE initial_clean_incomplete.
       ENDIF.
     ENDIF.
 
    READ TABLE lt_equi_material_details INTO lx_equi_material_details INDEX 1.
     "JCRAIG2904
     IF sy-subrc <> 0.
       "Proceed with initial values for equipment's first clean/use
     ENDIF.
 
    READ TABLE lt_equi_date_details INTO lx_equi_date_details INDEX 1.
     "JCRAIG2904
     IF sy-subrc <> 0.
       "Proceed with initial values for equipment's first clean/use
     ENDIF.
 
    "Append values to export tables
     APPEND l_equipment TO et_equi_id.
 
    SELECT SINGLE maktx
       FROM makt
       WHERE matnr = @lx_equi_material_details-material AND spras = @sy-langu
       INTO @l_stat_prod.
 
    IF sy-subrc <> 0.
       l_stat_prod = TEXT-010.
     ENDIF.
 
    "05/26 Request to see Part Number instead of material description
 *    APPEND l_stat_prod TO et_equi_prod.
     APPEND lx_equi_material_details-material TO et_equi_prod.
     APPEND lx_equipment-eqktx TO et_equi_desc.
     APPEND lx_equi_clean_details-status TO et_equi_stat.
     APPEND lx_equi_date_details-status_date TO et_equi_dats.
     APPEND lx_equipment-eqtyp TO et_equi_type.
 

    DATA: lv_cal_due_date TYPE d VALUE 00000000,
           lv_day          TYPE string VALUE '01',
           lv_equi_objek   TYPE cuobn,
           l_equi_filt     TYPE equnr.
 
    CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
       EXPORTING
         input  = l_equipment
       IMPORTING
         output = l_equi_filt.
 
    SELECT SINGLE inob~cuobj  "#EC "#EC CI_NOFIRST
       FROM inob
       INTO lv_equi_objek
       WHERE objek = l_equi_filt.
 
    "Get the calibration due date
     SELECT SINGLE ausp~atinn, cabn~atnam, ausp~atwrt
       FROM ausp
       LEFT OUTER JOIN cabn ON cabn~atinn = ausp~atinn
       INTO @DATA(lx_calib_due_date)
       WHERE ausp~objek = @lv_equi_objek
       AND ausp~atinn = @lc_equi_char.
 
    "If no calibration due date exists, equipment is not calibrated ignore append
     " otherwise append to parameter
     IF sy-subrc = 0.
       "Convert retrieved date into date stamp
       SPLIT lx_calib_due_date-atwrt AT '/' INTO DATA(lv_month) DATA(lv_year).
       CONCATENATE lv_year lv_month lv_day INTO DATA(lv_date_char).
       lv_cal_due_date = lv_date_char.
       APPEND lv_cal_due_date TO et_calib_due_date.
     ELSE.
       CLEAR lv_cal_due_date.
       APPEND lv_cal_due_date TO et_calib_due_date.
     ENDIF.
     CLEAR lv_equi_objek.
 
    CLEAR l_stat_prod.
   ENDLOOP.
 
*}   INSERT
 ENDFUNCTION.
