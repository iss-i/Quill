FUNCTION ZSMPL_FM_INCREMENT_TABLE_LINE .
 *"--------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_INDEX) TYPE  /SMPL/STR_TT_VORNR OPTIONAL
 *"     REFERENCE(IV_FLAG) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(IV_ORDER) TYPE  AUFNR
 *"     REFERENCE(IV_CRID) TYPE  POC_DOCID
 *"     REFERENCE(IV_PHASE) TYPE  VORNR
 *"     REFERENCE(IV_STEP_INDEX) TYPE  INT4
 *"     REFERENCE(IV_KEYWORD) TYPE  CHAR10
 *"  EXPORTING
 *"     REFERENCE(EV_INDEX_T1) TYPE  /SMPL/STR_TT_VORNR
 *"     REFERENCE(EV_INDEX_T2) TYPE  /SMPL/STR_TT_VORNR
 *"--------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_INCREMENT_TABLE_LINE                          *
 * Created by      : Jason Craig                                            *
 * Supplier        : ISSI                                                   *
 * Created on      : July 24, 2024                                          *
 * Purpose         : Increment all table line indexes together              *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                       Jason Craig      07/25/2024    *
 *--------------------------------------------------------------------------*
 
DATA(lv_index) = iv_index.
 DATA:lt_index_data     TYPE TABLE OF ztc_store_index,
       lv_increment TYPE int4 VALUE 1,
       lt_table TYPE /SMPL/STR_TT_VORNR,
       lv_current_index_val TYPE int4.
 
"Get initial line index
 
CALL FUNCTION '/SMPL/PPPI_FM_SET_LINE_IDX'
   CHANGING
     ct_index       = lv_index.
 
  DATA(ls_index) = lines( iv_index ).
 
IF iv_flag = 'X'.
 *  **Pass the fetched Values
     APPEND VALUE #( proc_order  = iv_order       control_recipe = iv_crid
                     phase       = iv_phase       step_index     = iv_step_index
                     table_index = ls_index       keyword        = iv_keyword )
                     TO lt_index_data.
     CHECK lt_index_data[] IS NOT INITIAL.
 
**Insert tables with new entries
     IF lines( lt_index_data ) GT 0.
       MODIFY ztc_store_index FROM TABLE lt_index_data.
     ENDIF.
 ELSE.
   SELECT SINGLE MAX( table_index )  FROM ztc_store_index INTO @DATA(lv_current_index)
                         WHERE proc_order          = @iv_order
                         AND   control_recipe   = @iv_crid
                         AND   phase            = @iv_phase
                         AND   keyword          = @iv_keyword.
 
     lv_current_index_val = lv_current_index.
      lv_current_index_val = lv_current_index_val + 1.
 *     lv_current_index = lv_current_index + 1.
 
     WHILE lv_increment <= lv_current_index_val.
        APPEND lv_increment to lt_table.
        lv_increment = lv_increment + 1.
        ENDWHILE.
 
      ev_index_t1 = lt_table.
       ev_index_t2 = lt_table.
 ENDIF.
 
ENDFUNCTION.
