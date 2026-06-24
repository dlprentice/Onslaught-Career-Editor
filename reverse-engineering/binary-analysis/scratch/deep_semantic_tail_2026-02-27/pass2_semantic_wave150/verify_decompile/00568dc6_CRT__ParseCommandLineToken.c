/* address: 0x00568dc6 */
/* name: CRT__ParseCommandLineToken */
/* signature: int CRT__ParseCommandLineToken(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__ParseCommandLineToken(void)

{
  byte bVar1;
  int extraout_EAX;
  byte *pbVar2;
  byte *pbVar3;

  if (DAT_009d4608 == 0) {
    CDXTexture__Helper_0056836a();
  }
  bVar1 = *DAT_009d35f4;
  pbVar3 = DAT_009d35f4;
  if (bVar1 == 0x22) {
    while( true ) {
      pbVar2 = pbVar3;
      bVar1 = pbVar2[1];
      pbVar3 = pbVar2 + 1;
      if ((bVar1 == 0x22) || (bVar1 == 0)) break;
      CTexture__Helper_0056d21c((uint)bVar1);
      if (extraout_EAX != 0) {
        pbVar3 = pbVar2 + 2;
      }
    }
    if (*pbVar3 == 0x22) goto LAB_00568e03;
  }
  else {
    while (0x20 < bVar1) {
      bVar1 = pbVar3[1];
      pbVar3 = pbVar3 + 1;
    }
  }
  for (; (*pbVar3 != 0 && (*pbVar3 < 0x21)); pbVar3 = pbVar3 + 1) {
LAB_00568e03:
  }
  return (int)pbVar3;
}
