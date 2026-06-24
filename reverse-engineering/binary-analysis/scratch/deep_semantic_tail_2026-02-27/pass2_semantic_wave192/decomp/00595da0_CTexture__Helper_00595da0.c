/* address: 0x00595da0 */
/* name: CTexture__Helper_00595da0 */
/* signature: void __stdcall CTexture__Helper_00595da0(void * param_1) */


void CTexture__Helper_00595da0(void *param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined1 *puVar3;
  int iVar4;

  iVar4 = *(int *)((int)param_1 + 0x14);
  if (iVar4 != 100) {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 0x14;
    puVar1[6] = iVar4;
    (*(code *)*puVar1)(param_1);
  }
  if (*(int *)((int)param_1 + 0x44) == 0) {
    uVar2 = (*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,0,0x348);
    *(undefined4 *)((int)param_1 + 0x44) = uVar2;
  }
  *(undefined4 *)((int)param_1 + 0x38) = 8;
  CTexture__Helper_00595550(param_1,0,0x5eecd8,0x32,1);
  CTexture__Helper_00595550(param_1,1,0x5eebd8,0x32,1);
  CTexture__Helper_005958e0();
  puVar3 = (undefined1 *)((int)param_1 + 0x88);
  iVar4 = 0x10;
  do {
    puVar3[-0x10] = 0;
    *puVar3 = 1;
    puVar3[0x10] = 5;
    puVar3 = puVar3 + 1;
    iVar4 = iVar4 + -1;
  } while (iVar4 != 0);
  *(undefined4 *)((int)param_1 + 0xac) = 0;
  *(undefined4 *)((int)param_1 + 0xa8) = 0;
  *(undefined4 *)((int)param_1 + 0xb0) = 0;
  *(undefined4 *)((int)param_1 + 0xb4) = 0;
  *(undefined4 *)((int)param_1 + 0xb8) = 0;
  if (8 < *(int *)((int)param_1 + 0x38)) {
    *(undefined4 *)((int)param_1 + 0xb8) = 1;
  }
  *(undefined4 *)((int)param_1 + 0xbc) = 0;
  *(undefined4 *)((int)param_1 + 0xc0) = 0;
  *(undefined4 *)((int)param_1 + 0xc4) = 0;
  *(undefined4 *)((int)param_1 + 200) = 0;
  *(undefined4 *)((int)param_1 + 0xcc) = 0;
  *(undefined1 *)((int)param_1 + 0xd4) = 1;
  *(undefined1 *)((int)param_1 + 0xd5) = 1;
  *(undefined1 *)((int)param_1 + 0xd6) = 0;
  *(undefined2 *)((int)param_1 + 0xd8) = 1;
  *(undefined2 *)((int)param_1 + 0xda) = 1;
  CTexture__Helper_00595c10(param_1);
  return;
}
