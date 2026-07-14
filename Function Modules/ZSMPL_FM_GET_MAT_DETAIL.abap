FUNCTION ZSMPL_FM_GET_MAT_DETAIL.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_MATNR) TYPE  MATNR
 *"  EXPORTING
 *"     REFERENCE(EX_MAT_DESC) TYPE  MAKTX
 *"     REFERENCE(EX_UOM) TYPE  MEINS
 *"  EXCEPTIONS
 *"      MAT_DESC_DNE_FOR_LANGU
 *"      UOM_NOT_FOUND
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_GET_MAT_DETAIL                       *
 * Project/Ticket  : SMPL / NA                                          *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : KWVP774 Jason Craig                                *
 * Functional -                                                         *
 * Analyst         : KVHZ810 Frieda vd Merwe                            *
 * Create Date     : 14.04.2026                                         *
 * Description     : Retrieve Material Description & Base UOM from      *
 *                   importing material number                          *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
DATA: lv_matnr    TYPE matnr,
       lv_mat_desc TYPE maktx,
       lv_uom      TYPE meins.
 
  lv_matnr = im_matnr.
 
  SELECT SINGLE maktx FROM makt
     WHERE matnr = @lv_matnr
     AND spras = @sy-langu
     INTO @lv_mat_desc.
 
  IF sy-subrc <> 0.
     SELECT SINGLE maktx FROM makt
     WHERE matnr = @lv_matnr
     AND spras = 'E'
     INTO @lv_mat_desc.
   ENDIF.
 
  SELECT SINGLE meins FROM mara
     WHERE matnr = @lv_matnr INTO @lv_uom.
 
  IF sy-subrc <> 0.
     RAISE uom_not_found.
   ENDIF.
 
  ex_mat_desc = lv_mat_desc.
   ex_uom = lv_uom.
 



ENDFUNCTION.
