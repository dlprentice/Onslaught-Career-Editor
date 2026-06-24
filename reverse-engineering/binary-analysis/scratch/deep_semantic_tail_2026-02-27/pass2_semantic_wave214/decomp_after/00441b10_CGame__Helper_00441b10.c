/* address: 0x00441b10 */
/* name: CGame__Helper_00441b10 */
/* signature: void __cdecl CGame__Helper_00441b10(void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CGame__Helper_00441b10(void *param_1,int param_2)

{
  if (param_1 != (void *)0x0) {
    _DAT_0066eb80 = *(undefined4 *)param_1;
    DAT_0066eb84 = *(undefined4 *)((int)param_1 + 4);
    _DAT_0066eb88 = *(undefined4 *)((int)param_1 + 8);
    _DAT_0066eb8c = *(undefined4 *)((int)param_1 + 0xc);
    DAT_0066ff74 = 1;
    DAT_0066ff75 = (undefined1)param_2;
    return;
  }
  DAT_0066eb84 = 0xffffffff;
  _DAT_0066eb80 = 0;
  DAT_0066ff74 = 1;
  DAT_0066ff75 = (undefined1)param_2;
  return;
}
