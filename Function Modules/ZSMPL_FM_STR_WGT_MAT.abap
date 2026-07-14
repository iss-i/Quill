FUNCTION ZSMPL_FM_STR_WGT_MAT.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_CONTROL_RECIPE) TYPE  POC_DOCID
 *"     REFERENCE(IV_MATERIAL) TYPE  MATNR OPTIONAL
 *"     REFERENCE(IV_MATERIAL_DESC) TYPE  MAKTX
 *"     REFERENCE(IV_QTY) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(IV_UOM) TYPE  MEINS OPTIONAL
 *"     REFERENCE(IV_MATERIAL_ALT) TYPE  MATNR OPTIONAL
 *"     REFERENCE(IV_ITEM_NR) TYPE  APOSN OPTIONAL
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_STR_WGT_MAT                               *
 * Project/Ticket  : SMPL / NA                                          *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : KWVP774 Jason Craig                                *
 * Functional -                                                         *
 * Analyst         : KVHZ810 Frieda vd Merwe                            *
 * Create Date     : 14.04.2026                                         *
 * Description     : Store weighed out material quantities for BOM      *
 *                   materials and additional/alternate materials -     *
 *                   aggregate total qty if the same material is issued *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
  DATA: ls_weight TYPE ztc_wt_mat,
         lv_mat    TYPE matnr,
         lv_qty_acc TYPE erfmg VALUE 0.
 
  "JCRAIG 20250929 - Allow for alternates
   IF iv_material = iv_material_alt.
     lv_mat = iv_material.
   ELSEIF iv_material_alt IS INITIAL.
     lv_mat = iv_material.
   ELSE.
     lv_mat = iv_material_alt.
   ENDIF.
 
  " Assign importing parameters to ztc_wt_mat structure
   ls_weight-control_recipe = iv_control_recipe.
   ls_weight-material = lv_mat.
   ls_weight-material_desc = iv_material_desc.
   ls_weight-weighed_qty = iv_qty.
   ls_weight-uom = iv_uom.
   ls_weight-item_nr = iv_item_nr.
 
  SELECT SINGLE weighed_qty FROM ztc_wt_mat
     WHERE control_recipe = @iv_control_recipe
     AND material = @lv_mat
     INTO @DATA(lv_qty).
 
  IF sy-subrc = 0.
    " Aggregate quantities for duplicate materials
    lv_qty_acc = lv_qty + iv_qty.
    ls_weight-weighed_qty = lv_qty_acc.
 
   MODIFY ztc_wt_mat FROM ls_weight.
 
  ELSE.
 
* Insert ls_weight into ztc_az_weight custom table)
    INSERT ztc_wt_mat FROM ls_weight.
 
  ENDIF.
 


ENDFUNCTION.
