/* address: 0x00542990 */
/* name: CDXEngine__Unk_00542990 */
/* signature: void CDXEngine__Unk_00542990(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXEngine__Unk_00542990(void)

{
  undefined4 *puVar1;
  undefined4 *obj;

  puVar1 = DAT_0067a678;
  while (obj = puVar1, obj != (undefined4 *)0x0) {
    puVar1 = (undefined4 *)*obj;
    if (obj != (undefined4 *)0x0) {
      if ((void *)obj[0xf] != (void *)0x0) {
        OID__FreeObject((void *)obj[0xf]);
        obj[0xf] = 0;
      }
      DAT_008aa8bc = DAT_008aa8bc + -1;
      OID__FreeObject(obj);
    }
  }
  DAT_0067a678 = (undefined4 *)0x0;
  if (DAT_008aa8cc != 0) {
    CDXEngine__Helper_00501310(DAT_008aa8cc);
    DAT_008aa8cc = 0;
  }
  if (DAT_008aa8b4 != 0) {
    CDXEngine__Helper_00501310(DAT_008aa8b4);
    DAT_008aa8b4 = 0;
  }
  if (DAT_008aa8b8 != 0) {
    CHud__Helper_004f27e0(DAT_008aa8b8 + 8);
    DAT_008aa8b8 = 0;
  }
  _DAT_008aa8c0 = 0;
  _DAT_008aa8c4 = 0;
  return;
}
