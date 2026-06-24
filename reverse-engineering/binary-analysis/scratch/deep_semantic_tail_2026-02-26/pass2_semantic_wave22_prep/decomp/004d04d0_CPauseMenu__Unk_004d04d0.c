/* address: 0x004d04d0 */
/* name: CPauseMenu__Unk_004d04d0 */
/* signature: void CPauseMenu__Unk_004d04d0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CPauseMenu__Unk_004d04d0(void)

{
  if (DAT_0082b490 != (int *)0x0) {
    CHud__Helper_004f27e0((int)DAT_0082b490 + 8);
    DAT_0082b490 = (int *)0x0;
  }
  DAT_0082b490 = CTexture__FindTexture(s_FrontEnd_v2_FE_Blank_tga_00629f68,4,0,1,0,1);
  return;
}
