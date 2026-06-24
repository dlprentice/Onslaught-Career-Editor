/* address: 0x00565bcb */
/* name: CRT__BuildCompositeLocaleString */
/* signature: int CRT__BuildCompositeLocaleString(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__BuildCompositeLocaleString(void)

{
  bool bVar1;
  int iVar2;
  undefined **ppuVar3;
  undefined **ppuVar4;

  bVar1 = true;
  if (DAT_00653d34 == (undefined1 *)0x0) {
    DAT_00653d34 = _malloc(0x351);
  }
  *DAT_00653d34 = 0;
  CTexture__Helper_00565d9c((int)DAT_00653d34,3);
  ppuVar3 = &PTR_DAT_00653d40;
  do {
    CDXTexture__Helper_00567df0(DAT_00653d34,&DAT_005e5e24);
    ppuVar4 = ppuVar3 + 3;
    iVar2 = _strcmp(*ppuVar3,ppuVar3[3]);
    if (iVar2 != 0) {
      bVar1 = false;
    }
    CTexture__Helper_00565d9c((int)DAT_00653d34,3);
    ppuVar3 = ppuVar4;
  } while ((int)ppuVar4 < 0x653d70);
  if (!bVar1) {
    return (int)DAT_00653d34;
  }
  CRT__FreeBase((int)DAT_00653d34);
  DAT_00653d34 = (undefined1 *)0x0;
  return (int)PTR_DAT_00653d4c;
}
