/* address: 0x004685a0 */
/* name: CFrontEnd__SetRenderViewAndProjection */
/* signature: void CFrontEnd__SetRenderViewAndProjection(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CFrontEnd__SetRenderViewAndProjection(void)

{
  undefined1 *puStack_44;
  undefined1 local_40 [12];
  float afStack_34 [13];

  puStack_44 = local_40;
  (*(code *)*DAT_0089d760)();
  CFrontEnd__Helper_00449ef0(&DAT_0089d760);
  CDXEngine__SetViewAndProjection(&DAT_009c65c0,afStack_34,(float *)&puStack_44);
  return;
}
