REPORT zsmpl_pp_delete_data.
*&---------------------------------------------------------------------*
*& ZSMPL_PP_DELETE_DATA  -  Delete data from the process-parameter tables
*&   ZTC_PP_PVAL / ZTC_PP_PARAM / ZTC_PP_RES / ZTC_PP_UOP
*& Package : ZSMPL_AZP2
*&
*& Companion to the ZSMPL_PP_LOAD_* programs - clears loaded data so a
*& load can be re-run from scratch.
*&
*& *** THIS DELETES DATA. Read before running. ***
*&   p_test = 'X' (DEFAULT) -> simulation. Nothing is deleted; the report
*&                             shows how many rows WOULD be deleted.
*&   p_conf                 -> must ALSO be ticked to actually delete.
*&                             (untick p_test AND tick p_conf)
*&
*& Scope:
*&   - Tick only the tables you want to clear (all four default to on).
*&   - s_uop (optional) restricts to one/some unit operations. Leave it
*&     EMPTY to clear every row in the selected tables (current client).
*&
*& Deletion runs in dependency order:  PVAL -> PARAM -> RES -> UOP
*& (values first, masters last) so nothing is orphaned mid-run.
*&---------------------------------------------------------------------*
* NOTE: gv_t1/gv_t2/gv_t3 are declared automatically by the
* SELECTION-SCREEN ... TITLE statements - do NOT add DATA for them.

DATA: gs_pval TYPE ztc_pp_pval.        "reference for the SELECT-OPTION

SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE gv_t1.
PARAMETERS: p_pval  AS CHECKBOX DEFAULT 'X',
            p_param AS CHECKBOX DEFAULT 'X',
            p_res   AS CHECKBOX DEFAULT 'X',
            p_uop   AS CHECKBOX DEFAULT 'X'.
SELECTION-SCREEN END OF BLOCK b1.

SELECTION-SCREEN BEGIN OF BLOCK b2 WITH FRAME TITLE gv_t2.
SELECT-OPTIONS s_uop FOR gs_pval-uop_id.
SELECTION-SCREEN END OF BLOCK b2.

SELECTION-SCREEN BEGIN OF BLOCK b3 WITH FRAME TITLE gv_t3.
PARAMETERS: p_test AS CHECKBOX DEFAULT 'X',
            p_conf AS CHECKBOX DEFAULT ' '.
SELECTION-SCREEN END OF BLOCK b3.

DATA: gv_pval  TYPE i,
      gv_param TYPE i,
      gv_res   TYPE i,
      gv_uop   TYPE i.

INITIALIZATION.
  gv_t1 = 'Tables to clear'.
  gv_t2 = 'Optional scope (leave empty = all rows)'.
  gv_t3 = 'Execution - test first!'.

AT SELECTION-SCREEN.
  IF p_pval = abap_false AND p_param = abap_false
     AND p_res = abap_false AND p_uop = abap_false.
    MESSAGE 'Select at least one table to clear' TYPE 'E'.
  ENDIF.
  IF p_test = abap_false AND p_conf = abap_false.
    MESSAGE 'Update mode requires the "Confirm deletion" flag' TYPE 'E'.
  ENDIF.

START-OF-SELECTION.
  PERFORM process.
  PERFORM log.

*&--- count (test) or delete (update), in dependency order ------------*
FORM process.

* 1) Values
  IF p_pval = abap_true.
    SELECT COUNT(*) FROM ztc_pp_pval WHERE uop_id IN @s_uop INTO @gv_pval.
    IF p_test = abap_false.
      DELETE FROM ztc_pp_pval WHERE uop_id IN @s_uop.
      gv_pval = sy-dbcnt.
    ENDIF.
  ENDIF.

* 2) Parameter catalog
  IF p_param = abap_true.
    SELECT COUNT(*) FROM ztc_pp_param WHERE uop_id IN @s_uop INTO @gv_param.
    IF p_test = abap_false.
      DELETE FROM ztc_pp_param WHERE uop_id IN @s_uop.
      gv_param = sy-dbcnt.
    ENDIF.
  ENDIF.

* 3) Resource master
  IF p_res = abap_true.
    SELECT COUNT(*) FROM ztc_pp_res WHERE uop_id IN @s_uop INTO @gv_res.
    IF p_test = abap_false.
      DELETE FROM ztc_pp_res WHERE uop_id IN @s_uop.
      gv_res = sy-dbcnt.
    ENDIF.
  ENDIF.

* 4) Unit-operation master
  IF p_uop = abap_true.
    SELECT COUNT(*) FROM ztc_pp_uop WHERE uop_id IN @s_uop INTO @gv_uop.
    IF p_test = abap_false.
      DELETE FROM ztc_pp_uop WHERE uop_id IN @s_uop.
      gv_uop = sy-dbcnt.
    ENDIF.
  ENDIF.

  IF p_test = abap_false.
    COMMIT WORK AND WAIT.
  ENDIF.

ENDFORM.

*&--- summary log ----------------------------------------------------*
FORM log.
  DATA lv_total TYPE i.

  WRITE: / 'Process Parameter Tables - Deletion'.
  ULINE.
  IF p_test = abap_true.
    WRITE: / 'Mode        : TEST (simulation - NOTHING deleted)'.
  ELSE.
    WRITE: / 'Mode        : UPDATE (rows deleted and committed)'.
  ENDIF.
  IF s_uop[] IS INITIAL.
    WRITE: / 'Scope       : ALL unit operations (current client)'.
  ELSE.
    WRITE: / 'Scope       : restricted by UOP_ID selection'.
  ENDIF.
  SKIP.

  IF p_test = abap_true.
    WRITE: / 'Rows that WOULD be deleted:'.
  ELSE.
    WRITE: / 'Rows deleted:'.
  ENDIF.

  IF p_pval = abap_true.
    WRITE: / '  ZTC_PP_PVAL  (values)   :', gv_pval.
  ENDIF.
  IF p_param = abap_true.
    WRITE: / '  ZTC_PP_PARAM (catalog)  :', gv_param.
  ENDIF.
  IF p_res = abap_true.
    WRITE: / '  ZTC_PP_RES   (resources):', gv_res.
  ENDIF.
  IF p_uop = abap_true.
    WRITE: / '  ZTC_PP_UOP   (unit ops) :', gv_uop.
  ENDIF.

  lv_total = gv_pval + gv_param + gv_res + gv_uop.
  ULINE.
  WRITE: / '  TOTAL                   :', lv_total.

  IF p_test = abap_true.
    SKIP.
    WRITE: / 'Nothing was changed. To delete: untick "Test run" AND tick',
             '"Confirm deletion".'.
  ENDIF.
ENDFORM.
