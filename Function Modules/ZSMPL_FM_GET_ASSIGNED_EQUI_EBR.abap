FUNCTION zsmpl_fm_get_assigned_equi_ebr .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_ORDER) TYPE  AUFNR
 *"     REFERENCE(IM_EQUIP_TYPE) TYPE  EQTYP
 *"     REFERENCE(IM_ALLOW_NA) TYPE  BOOLE_D OPTIONAL
 *"     REFERENCE(IM_VORNR) TYPE  VORNR OPTIONAL
 *"     REFERENCE(IM_OBJ_TYP) TYPE  EQART OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EX_EQUI) TYPE  CHAR30
 *"     REFERENCE(EX_EQUI_TXT) TYPE  CHAR30
 *"  EXCEPTIONS
 *"      INTERNAL_ERROR
 *"----------------------------------------------------------------------
 * Program Name    : /SMPL/ELB_FM_GET_ASSIGNED_EQUI                         *
 * Created by      : Karl Maritz (KMARITZ)                                  *
 * Supplier        : Pangaea Solutions Inc. (PSi)                           *
 * Created on      : January 1, 2024                                        *
 *    Analyst:     : N/A                                                    *
 * Purpose         : Returns assigned order equipment or prompts user with  *
 *                   pop-up to select equipment if multiples have been      *
 *                   assigned to the order                                  *
 * Modifications                                                            *
 *--------------------------------------------------------------------------*
 *  MOD1 - Add STANDARDIZATION_CHECK for equipment that follows stand.      *
 *         workflow (GGROTIUS 20250805)                                     *
 *  MOD2 - Allow for technical object type selection                        *
 *  MOD3 - Allow for Multi-PO Assignment                                    *
 *  MOD4 - Add dynamic status retrieval to allow for translation (20260119) *
 *--------------------------------------------------------------------------*
   TYPES:
     "Equipment (Rooms) data
     BEGIN OF lty_equi_results,
       equi_id  TYPE char30,
       equi_txt TYPE char30,
       status   TYPE char30,
     END OF lty_equi_results.
 
  CONSTANTS: lc_scale_na        TYPE char30 VALUE 'NA',
              lc_message_warn    TYPE char20 VALUE 'ICON_MESSAGE_WARNING',
              lc_warn_txt        TYPE sta_text VALUE 'WARNING',
              lc_stat_in_use     TYPE char2  VALUE 'U1',
              lc_iuc             TYPE char2  VALUE 'U2'.
 
  DATA: lt_equi_results     TYPE TABLE OF lty_equi_results,
         lx_equi_results     LIKE LINE OF lt_equi_results,
         lt_equi_results_fin TYPE TABLE OF lty_equi_results,
 
        lr_table            TYPE REF TO cl_salv_table,
         lr_selections       TYPE REF TO cl_salv_selections,
         lo_cols             TYPE REF TO cl_salv_columns_table,
         lo_column           TYPE REF TO cl_salv_column,
 
        l_id                TYPE icon-id,
 
        l_popup_title       TYPE char10,
         lv_title            TYPE string,
         lt_use_stats        TYPE /smpl/str_tt_equi_stat,  "MOD3.
         lv_assigned_status  TYPE /smpl/str_de_equi_stat,  "MOD4
         lv_iuc  TYPE /smpl/str_de_equi_stat.  "MOD4
 

  DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ). "zcl_smpl_ebr_apc_ws( ).
   DATA: lo_socket           TYPE REF TO /smpl/ebr_cl_web_sock_hndl, "zcl_smpl_ebr_web_socket_handle,
         ls_valuehelp_string TYPE string.
 
  "MOD4 - Start
   "Clear export parameters
   CLEAR: ex_equi,ex_equi_txt.
 
    "Clear & refresh variables/tables - MOD4
   CLEAR: lx_equi_results, l_id, lv_assigned_status, l_popup_title.
   REFRESH: lt_equi_results, lt_equi_results_fin, lt_use_stats.
 
  "Get IN USE status
   PERFORM get_eq_stat_by_class USING lc_stat_in_use abap_false CHANGING lt_use_stats.
   READ TABLE lt_use_stats INDEX 1 INTO lv_assigned_status.
   IF sy-subrc <> 0.
     "Handled by status table configuration in preceding FMs
   ENDIF.
 
    "Get IN USE CLEANED status
   CLEAR lt_use_stats.
   PERFORM get_eq_stat_by_class USING lc_iuc abap_false CHANGING lt_use_stats.
   READ TABLE lt_use_stats INDEX 1 INTO lv_iuc.
   IF sy-subrc <> 0.
     "Handled by status table configuration in preceding FMs
   ENDIF.
   "MOD4 End
 
  CREATE OBJECT lo_socket.
 
  "Set warning pop-up title
   l_popup_title =  'Warning'(017).
 
  "Get Warning Icon
   SELECT id
     FROM icon
     INTO l_id
     WHERE name = lc_message_warn
     ORDER BY PRIMARY KEY
     .
   ENDSELECT.
 
  "Put N/A in list if no scales are connected
   IF im_allow_na EQ abap_true.
     APPEND VALUE lty_equi_results(
       equi_id = TEXT-010
       equi_txt = TEXT-010
       status = lv_assigned_status ) TO lt_equi_results.
   ENDIF.
 
  "Adding change to select only entries where Confirmation signature has been completed 20250414
   SELECT master~equi_id, master~equi_txt, master~status
     FROM /smpl/elb_equip AS master
     INNER JOIN equi ON equi~equnr = master~equi_id
     LEFT OUTER JOIN eqkt ON equi~equnr = eqkt~equnr AND eqkt~spras = @sy-langu  "MOD4
     WHERE master~order_num = @im_order
           "202505 JCRAIG Addition for order-phase combo
           AND ( @im_vornr IS NULL OR activity = @im_vornr )
           AND ( equi~eqtyp IS NULL OR equi~eqtyp = @im_equip_type )
           AND master~updat_cb <> ''
           AND ( @im_obj_typ IS NULL OR equi~eqart = @im_obj_typ )  "MOD2
     ORDER BY master~equi_id, master~entry_num DESCENDING
     APPENDING CORRESPONDING FIELDS OF TABLE @lt_equi_results.
   IF sy-subrc = 0.
     "Grab the latest record
     IF lt_equi_results IS NOT INITIAL.
       DELETE ADJACENT DUPLICATES FROM lt_equi_results COMPARING equi_id.
     ENDIF.
   ENDIF.
 
  "Delete entries with order status not equal to "Assigned"
   DELETE lt_equi_results WHERE status <> lv_assigned_status AND status <> lv_iuc.
 
*Display Rooms Options
 
  "If only one Room is assigned, then no pop-up is required - just
   "return the Room details.
   IF lines( lt_equi_results ) EQ 1
       AND im_allow_na NE abap_true .
     READ TABLE lt_equi_results INTO lx_equi_results INDEX 1.
     "If no scales are found, display a warning message
   ELSEIF    lines( lt_equi_results ) EQ 0
       OR ( lines( lt_equi_results ) EQ 1
             AND im_allow_na EQ abap_true ).
 *** Enhancement for smpl EBR
     DATA: lv_return TYPE abap_bool.
     CALL METHOD /smpl/ebr_cl_enh_fwk=>get_entry
       EXPORTING
         iv_key1  = CONV #( 'SMPL_EBR' )
         iv_key2  = CONV #( 'GET_ASSIGNED_EQUI' )
       IMPORTING
         es_entry = DATA(ls_entry).
     DATA: lv_text TYPE string.
 
    IF ls_entry-class_name IS NOT INITIAL AND ls_entry-method_name IS NOT INITIAL.
       IF im_equip_type = 'R'.
         lv_text = 'No room is currently assigned to the EBR for this order'.
       ELSEIF  im_equip_type = 'A'.
         lv_text = 'This Additional Equipment Item has not been assigned to the EBR for this order'.
       ENDIF.
 *  *Passing the class parameters
       DATA(lt_ptab) = VALUE abap_parmbind_tab( ( name  = 'IM_TYPE'     kind  = cl_abap_objectdescr=>exporting value = REF #( 'W' ) )
                                                ( name = 'IM_MESSAGE' kind = cl_abap_objectdescr=>exporting value = REF #( lv_text ) )
                                                ( name  = 'EX_RETURN' kind  = cl_abap_objectdescr=>changing value = REF #( lv_return ) ) ).
 *  *Attempting to call the class maintained with the appropriate parameters
       TRY.
           CALL METHOD (ls_entry-class_name)=>(ls_entry-method_name)
             PARAMETER-TABLE
             lt_ptab.
 *  *Catching all the possible exceptions that could lead to a dump and
 *rasing an error
         CATCH cx_sy_no_handler cx_sy_dyn_call_illegal_method
               cx_sy_dyn_call_illegal_type
               cx_sy_dyn_call_param_missing cx_sy_dyn_call_param_not_found cx_root.
           RAISE internal_error.
       ENDTRY.
       ex_equi = TEXT-010.
       ex_equi_txt = TEXT-010.
       IF lv_return = 'X'.
         RETURN.
       ENDIF.
 
    ENDIF.
 ** enhancement for simpl EBR.
     IF im_equip_type = 'R'.
       "Display Warning Mesage
       CALL FUNCTION 'POPUP_TO_INFORM'
         EXPORTING
           titel = l_popup_title
           txt1  = l_id
           txt2  = 'No room is currently assigned to the EBR for this order'(003).
     ELSEIF im_equip_type = 'A'.
       "Display Warning Mesage
       CALL FUNCTION 'POPUP_TO_INFORM'
         EXPORTING
           titel = l_popup_title
           txt1  = l_id
           txt2  = 'This Additional Equipment Item has not been assigned to the EBR for this order'(004).
     ENDIF.
 
    ex_equi = lc_scale_na.
     ex_equi_txt = lc_scale_na.
 
    RETURN.
   ELSE.
     LOOP AT lt_equi_results INTO lx_equi_results.
       SHIFT lx_equi_results-equi_id LEFT DELETING LEADING '0'.
       APPEND lx_equi_results TO lt_equi_results_fin.
     ENDLOOP.
 
    "KWVP774 Addition
     lx_equi_results-equi_id = TEXT-010.
     lx_equi_results-equi_txt = TEXT-010.
     APPEND lx_equi_results TO lt_equi_results_fin.
     "KWVP774
 

    IF  lcl_websocket->gv_function = 'SMPL_EBR' .
 
      IF lcl_websocket->gv_item_id IS INITIAL.
         ls_valuehelp_string =  '1-Equip ID;2-Description;3-Status'.
         lv_title = TEXT-022.
         CALL METHOD /smpl/ebr_cl_generic_val_help=>build_generic_param_value_help
           EXPORTING
             im_header_det = ls_valuehelp_string
             im_item_det   = lt_equi_results_fin
             im_title      = lv_title
           CHANGING
             ex_return     = lv_return.
         IF lv_return EQ abap_true.
           RETURN.
         ENDIF.
       ELSE.
         READ TABLE lt_equi_results_fin INTO lx_equi_results WITH KEY equi_id = lcl_websocket->gv_item_id. "lcl_websocket->gv_equipment_id.
         CLEAR lcl_websocket->gv_item_id. "lcl_websocket->gv_equipment_id.
       ENDIF.
     ELSE.
 
      "Multiple rooms where found, therefore a pop-up is required
       "for user input
       TRY.
           " Prepare table popup
           cl_salv_table=>factory(
             EXPORTING
               list_display = ' '
             IMPORTING
               r_salv_table = lr_table
             CHANGING
               t_table      = lt_equi_results_fin ).
 
          " Set header text for custom columns
           lo_cols = lr_table->get_columns( ).
 
          " Hide SAP Equipment Column
           lo_column = lo_cols->get_column( 'EQUI_ID' ).
           lo_column->set_medium_text( 'Equip. ID'(011) ).
           lo_column->set_long_text( 'Equip. ID'(011) ).
           lo_column->set_short_text( 'Eq. ID'(011) ).
 
          lo_column = lo_cols->get_column( 'EQUI_TXT' ).
           lo_column->set_medium_text( 'Description'(013) ).
           lo_column->set_long_text( 'Description'(013) ).
           lo_column->set_short_text( 'Descr.'(012) ).
 
          "Hide the Order Status column
           lo_column = lo_cols->get_column( 'STATUS' ).
           lo_column->set_visible( value  = if_salv_c_bool_sap=>false ).
 
        CATCH cx_root INTO DATA(lx_root).
           "Display Error Mesage
           CALL FUNCTION 'POPUP_TO_INFORM'
             EXPORTING
               titel = 'Error'(018)
               txt1  = l_id
               txt2  = lx_root->get_text( ).
           RETURN.
       ENDTRY.
 
      " Setup table
       lr_table->set_screen_popup(
       start_column = 1
       end_column   = 140
       start_line   = 1
       end_line     = 20 ).
       lr_selections = lr_table->get_selections( ).
       lr_selections->set_selection_mode(
         if_salv_c_selection_mode=>single ).
 
      " Shop popup
       lr_table->display( ).
 
      " Get selected rows, there should only be one
       DATA(lt_selected_row) = lr_selections->get_selected_rows( ).
       IF lines( lt_selected_row ) GT 1.
         RETURN.
       ENDIF.
 
      " Get first selected row information
       READ TABLE lt_selected_row INTO DATA(l_selected_row) INDEX 1.
 
      " This will allow the user pressing enter immediately to
       "automatically select the first line
       l_selected_row = COND #( WHEN l_selected_row EQ 0 THEN 1
         ELSE l_selected_row ).
 
*    " Get data in the first selected row
       READ TABLE lt_equi_results_fin INTO lx_equi_results
        INDEX l_selected_row.  "INDEX 1.
 
    ENDIF.
   ENDIF.
 
*Display Room values within respective columns
   ex_equi = lx_equi_results-equi_id.
 
  SHIFT ex_equi LEFT DELETING LEADING '0'.
 
  ex_equi_txt = lx_equi_results-equi_txt.
 

  "MOD1 Start - STANDARDIZATION_CHECK addition
   DATA: l_equnr       TYPE equnr,
         l_error       TYPE char2,
         l_warning_txt TYPE string.
 
  l_equnr = lx_equi_results-equi_id.
 
    CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
       EXPORTING
         input  = l_equnr
       IMPORTING
         output = l_equnr.
 
  PERFORM standardization_check USING l_equnr l_error.
   "If equipment is not standardized
   IF l_error EQ 'S1'.
     "Build warning message
     SHIFT l_equnr LEFT DELETING LEADING '0'.
     l_warning_txt = TEXT-019 && ` ` && l_equnr && ` ` && TEXT-021.
 
    CALL FUNCTION 'POPUP_TO_INFORM'
       EXPORTING
         titel = lc_warn_txt
         txt1  = l_id
         txt2  = l_warning_txt.
 
    ex_equi = TEXT-010.
     ex_equi_txt = TEXT-010.
 
    "If equipment has not been standardized, inform operator
   ELSEIF l_error EQ 'S2'.
     "Build warning message
     SHIFT l_equnr LEFT DELETING LEADING '0'.
     l_warning_txt = TEXT-019 && ` ` && l_equnr && ` ` && TEXT-020.
 
    CALL FUNCTION 'POPUP_TO_INFORM'
       EXPORTING
         titel = lc_warn_txt
         txt1  = l_id
         txt2  = l_warning_txt.
 
    ex_equi = TEXT-010.
     ex_equi_txt = TEXT-010.
   ENDIF.
   "MOD1 End
 
ENDFUNCTION.
 
"20250620 Generic subroutine to retrieve status based on class
 FORM get_eq_stat_by_class
   USING    iv_class         TYPE /smpl/str_de_stat_class
            iv_use_prefix    TYPE abap_bool
   CHANGING et_eq_stat       TYPE /smpl/str_tt_equi_stat.
 
  DATA: lt_result TYPE /smpl/str_tt_equi_stat,
         lv_pattern TYPE /smpl/str_de_stat_class.
 
  IF iv_use_prefix = abap_true.
     lv_pattern = iv_class && '%'.
 
    SELECT eq_stat
       INTO TABLE lt_result
       FROM /smpl/elb_eqstat
       WHERE class LIKE lv_pattern.
   ELSE.
     SELECT eq_stat
       INTO TABLE lt_result
       FROM /smpl/elb_eqstat
       WHERE class = iv_class.
   ENDIF.
 
  et_eq_stat = lt_result.
 
ENDFORM.
