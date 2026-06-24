/* address: 0x00590ea0 */
/* name: CDXTexture__Helper_00590ea0 */
/* signature: int __stdcall CDXTexture__Helper_00590ea0(void * param_1) */


int CDXTexture__Helper_00590ea0(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;

  if (*(int *)((int)param_1 + 0x14) == 0xca) {
    CTexture__Helper_0059b4d0((int)param_1);
    if (*(int *)((int)param_1 + 0x40) != 0) {
      *(undefined4 *)((int)param_1 + 0x14) = 0xcf;
      return 1;
    }
    *(undefined4 *)((int)param_1 + 0x14) = 0xcb;
  }
  iVar3 = *(int *)((int)param_1 + 0x14);
  if (iVar3 != 0xcb) {
    if (iVar3 != 0xcc) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x14;
      puVar2[6] = iVar3;
      (*(code *)*puVar2)(param_1);
    }
    iVar3 = CTexture__Helper_00590da0();
    return iVar3;
  }
  if (*(int *)(*(int *)((int)param_1 + 0x1b8) + 0x10) != 0) {
    while( true ) {
      if (*(undefined4 **)((int)param_1 + 8) != (undefined4 *)0x0) {
        (*(code *)**(undefined4 **)((int)param_1 + 8))(param_1);
      }
      iVar3 = (*(code *)**(undefined4 **)((int)param_1 + 0x1b8))(param_1);
      if (iVar3 == 0) {
        return 0;
      }
      if (iVar3 == 2) break;
      iVar1 = *(int *)((int)param_1 + 8);
      if ((iVar1 != 0) && ((iVar3 == 3 || (iVar3 == 1)))) {
        iVar3 = *(int *)(iVar1 + 4) + 1;
        *(int *)(iVar1 + 4) = iVar3;
        if (*(int *)(iVar1 + 8) <= iVar3) {
          *(int *)(iVar1 + 8) = *(int *)((int)param_1 + 0x144) + *(int *)(iVar1 + 8);
        }
      }
    }
  }
  *(undefined4 *)((int)param_1 + 0x9c) = *(undefined4 *)((int)param_1 + 0x94);
  iVar3 = CTexture__Helper_00590da0();
  return iVar3;
}
