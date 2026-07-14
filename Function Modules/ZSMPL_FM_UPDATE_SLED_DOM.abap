FUNCTION ZSMPL_FM_UPDATE_SLED_DOM.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_MATNR) TYPE  MATNR OPTIONAL
 *"     REFERENCE(IV_CHARG) TYPE  CHARG_D OPTIONAL
 *"     REFERENCE(IV_WERKS) TYPE  WERKS_D OPTIONAL
 *"     REFERENCE(IV_DOM) TYPE  DATS OPTIONAL
 *"     REFERENCE(IV_SLED_FLAG) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(IV_SLED) TYPE  DATS OPTIONAL
 *"     REFERENCE(IV_UPDATE_FLAG) TYPE  CHAR1 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_EXPIRY) TYPE  DATS
 *"     REFERENCE(EV_SHELF_LIFE) TYPE  INT3
 *"  EXCEPTIONS
 *"      NO_SHELF_LIFE
 *"      UPDATE_FAILED
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_UPDATE_SLED_DOM                               *
 * Project/Ticket  : SMPL / NA                                          *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : KWVP774 Jason Craig                                *
 * Functional -                                                         *
 * Analyst         : KVHZ810 Frieda vd Merwe                            *
 * Create Date     : 14.04.2026                                         *
 * Description     : Update Date of Manufacture & Shelf Life Expiration *
 *                   date of current material/batch                     *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
  DATA: lv_shelf_life TYPE mara-mhdhb,
         lv_sled       TYPE dats,
         ls_batchattr  TYPE bapibatchatt,
         ls_batchattrx TYPE bapibatchattx,
         lt_return     TYPE TABLE OF bapiret2.
 
" Get Shelf Life
   SELECT SINGLE mhdhb
     INTO lv_shelf_life
     FROM mara
     WHERE matnr = iv_matnr.
 
  IF lv_shelf_life IS INITIAL.
     RAISE no_shelf_life.
   ELSE.
     ev_shelf_life = lv_shelf_life.
   ENDIF.
 

" Calculate SLED
   lv_sled = iv_sled.
   IF lv_sled = 0 OR lv_sled IS INITIAL.
     lv_sled = iv_dom + lv_shelf_life.
   ENDIF.
 
  ev_expiry = lv_sled.
 
  IF iv_update_flag IS NOT INITIAL.
 

     " Check Batch Exists (MCH1 or MCHA depending on config)
     SELECT SINGLE matnr
       FROM mch1
       WHERE matnr = @iv_matnr
         AND charg = @iv_charg
 *        AND werks = @iv_werks
       INTO @DATA(lv_dummy).
 
    IF sy-subrc <> 0.
       RAISE batch_not_found.
     ENDIF.
 

  " Update DOM (HSDAT) and SLED (VFDAT)
     UPDATE mch1
       SET hsdat = @iv_dom,
           vfdat = @lv_sled
       WHERE matnr = @iv_matnr
         AND charg = @iv_charg.
 *        AND werks = @iv_werks.
 
     IF sy-subrc <> 0.
        RAISE update_failed.
      ENDIF.
 
   ENDIF.
 

ENDFUNCTION.
