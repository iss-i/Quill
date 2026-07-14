FUNCTION zsmpl_fm_comp_addition_items.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_BOM_START) TYPE  CHAR4
 *"     REFERENCE(IV_BOM_END) TYPE  CHAR4
 *"     REFERENCE(IV_CONTROL_RECIPE) TYPE  POC_DOCID
 *"     REFERENCE(IV_ORDER) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(IV_FLAG) TYPE  CHAR1 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_MATERIAL) TYPE  /SMPL/STR_TT_MATNR
 *"     REFERENCE(EV_MATERIAL_DESC) TYPE  /SMPL/STR_TT_MAKTX
 *"     REFERENCE(EV_QTY) TYPE  /SMPL/STR_TT_QTY
 *"     REFERENCE(EV_UOM) TYPE  /SMPL/STR_TT_UOM
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_COMP_ADDITION_ITEMS                       *
 * Project/Ticket  : SMPL / NA                                          *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : KWVP774 Jason Craig                                *
 * Functional -                                                         *
 * Analyst         : KVHZ810 Frieda vd Merwe                            *
 * Create Date     : 14.04.2026                                         *
 * Description     : Retrieve Weighed out components & quantities for   *
 *                   the current order from the custom table ZTC_WT_MAT *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
  DATA: lt_weight     TYPE TABLE OF ztc_wt_mat,
         ls_weight     TYPE ztc_wt_mat.
 
*-----------------------------------------------------------------------
 * Get all the weighed out Materials and match the weighed out quantity
 * with acceptable BOM Item range for this step
 *-----------------------------------------------------------------------
 
    "Select material from the weighed out table
     SELECT *
       FROM ztc_wt_mat
       WHERE ztc_wt_mat~control_recipe = @iv_control_recipe
       AND ztc_wt_mat~item_nr > @iv_bom_start AND ztc_wt_mat~item_nr < @iv_bom_end
       INTO TABLE @lt_weight.
 
    "Only show material if it has already been weighed
     IF sy-subrc = 0.
       LOOP AT lt_weight INTO ls_weight.
         APPEND ls_weight-weighed_qty TO ev_qty.
         APPEND ls_weight-material TO ev_material.
         APPEND ls_weight-material_desc TO ev_material_desc.
         APPEND ls_weight-uom TO ev_uom.
       ENDLOOP.
     ENDIF.
 
ENDFUNCTION.
