FUNCTION ZSMPL_FM_GET_PO_PRODUCT_INFO.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_ORDER) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(IV_CURRENT_ORDER) TYPE  AUFNR OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_MATNR) TYPE  MATNR
 *"     REFERENCE(EV_BATCH) TYPE  CHARG_D
 *"     REFERENCE(EV_EXPIRY) TYPE  DATS
 *"  EXCEPTIONS
 *"      ORDER_NOT_FOUND
 *"      INCORRECT_MATERIAL
 *"      BATCH_EXPIRED
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_GET_PO_PRODUCT_INFO                       *
 * Project/Ticket  : SMPL / NA                                          *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : KWVP774 Jason Craig                                *
 * Functional -                                                         *
 * Analyst         : KVHZ810 Frieda vd Merwe                            *
 * Create Date     : 14.04.2026                                         *
 * Description     : Retrieve material, batch and expiry for importing  *
 *                   order numbers - compare products for multiple orders *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
TYPES: BEGIN OF lty_po_info,
         aufnr TYPE aufnr,
         matnr TYPE matnr,
         charg TYPE charg_d,
        END OF lty_po_info.
 
DATA: ls_po_info TYPE lty_po_info,
       lt_po_info TYPE TABLE OF lty_po_info.
 
CONSTANTS: lc_posnr TYPE posnr VALUE '0001'.
 
  " Select order information
   SELECT SINGLE aufnr, matnr, charg
     FROM afpo
     WHERE aufnr = @iv_order
     AND posnr = @lc_posnr
     INTO @ls_po_info.
 
  "If order is valid - Check batch expiry
   IF sy-subrc = 0.
     ev_matnr = ls_po_info-matnr.
     ev_batch = ls_po_info-charg.
 
    "Retrieve batch expiry
     SELECT SINGLE vfdat FROM mch1
       INTO @DATA(lv_exp_date)
       WHERE charg = @ls_po_info-charg
       AND matnr = @ls_po_info-matnr.
 
      "Check and validate Batch expiry
       IF sy-subrc = 0.
         ev_expiry = lv_exp_date.
         IF lv_exp_date < sy-datum.
           MESSAGE 'Batch Expired' TYPE 'S' DISPLAY LIKE 'E'.
 *          RAISE batch_expired.
         ENDIF.
       ENDIF.
 
    "Compare Current PO product to entered PO product (e.g. Top-Offs)
     IF iv_current_order IS NOT INITIAL.
       CLEAR ls_po_info.
       SELECT SINGLE aufnr, matnr, charg
         FROM afpo
         WHERE aufnr = @iv_current_order
         AND posnr = @lc_posnr
         INTO @ls_po_info.
       IF ls_po_info-matnr <> ev_matnr.
         MESSAGE 'Material of entered PO does not match the current product' TYPE 'S' DISPLAY LIKE 'E' RAISING incorrect_material.
       ENDIF.
     ENDIF.
 
  ELSE.
     "Incorrect order entry
     RAISE order_not_found.
   ENDIF.
 




ENDFUNCTION.
