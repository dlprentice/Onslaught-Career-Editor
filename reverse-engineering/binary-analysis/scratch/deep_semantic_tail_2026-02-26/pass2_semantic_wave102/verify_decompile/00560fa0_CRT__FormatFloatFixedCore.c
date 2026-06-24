/* address: 0x00560fa0 */
/* name: CRT__FormatFloatFixedCore */
/* signature: int __cdecl CRT__FormatFloatFixedCore(void * param_1, int param_2, void * param_3, int param_4) */


int __cdecl CRT__FormatFloatFixedCore(void *param_1,int param_2,void *param_3,int param_4)

{
  int iVar1;
  undefined1 *puVar2;

  iVar1 = *(int *)((int)param_3 + 4) + -1;
  if (((char)param_4 != '\0') && (iVar1 == param_2)) {
    puVar2 = (undefined1 *)((uint)(*(int *)param_3 == 0x2d) + iVar1 + (int)param_1);
    *puVar2 = 0x30;
    puVar2[1] = 0;
  }
  puVar2 = param_1;
  if (*(int *)param_3 == 0x2d) {
    *(undefined1 *)param_1 = 0x2d;
    puVar2 = (undefined1 *)((int)param_1 + 1);
  }
  if (*(int *)((int)param_3 + 4) < 1) {
    CFastVB__Helper_0056112b(puVar2,1);
    *puVar2 = 0x30;
    puVar2 = puVar2 + 1;
  }
  else {
    puVar2 = puVar2 + *(int *)((int)param_3 + 4);
  }
  if (0 < param_2) {
    CFastVB__Helper_0056112b(puVar2,1);
    *puVar2 = DAT_00653aa0;
    iVar1 = *(int *)((int)param_3 + 4);
    if (iVar1 < 0) {
      if (((char)param_4 != '\0') || (-iVar1 <= param_2)) {
        param_2 = -iVar1;
      }
      CFastVB__Helper_0056112b(puVar2 + 1,param_2);
      _memset(puVar2 + 1,0x30,param_2);
    }
  }
  return (int)param_1;
}
