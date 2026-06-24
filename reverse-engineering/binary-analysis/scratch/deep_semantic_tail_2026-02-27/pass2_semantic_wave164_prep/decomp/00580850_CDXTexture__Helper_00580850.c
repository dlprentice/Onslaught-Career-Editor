/* address: 0x00580850 */
/* name: CDXTexture__Helper_00580850 */
/* signature: int __stdcall CDXTexture__Helper_00580850(void * param_1, void * param_2) */


int CDXTexture__Helper_00580850(void *param_1,void *param_2)

{
  int iVar1;
  uint uVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int local_3c [7];
  uint local_20;
  uint local_1c;
  undefined4 *local_18;
  uint local_14;
  undefined4 *local_10;
  uint local_c;
  uint local_8;

  (**(code **)(*(int *)param_1 + 0x30))(param_1,local_3c);
  iVar1 = (**(code **)(*(int *)param_1 + 0x34))(param_1,&local_14,0,0);
  if (-1 < iVar1) {
    iVar1 = (**(code **)(*(int *)param_2 + 0x34))(param_2,&local_1c,0,0);
    if (-1 < iVar1) {
      if ((((local_3c[0] == 0x31545844) || (local_3c[0] == 0x32545844)) ||
          (local_3c[0] == 0x33545844)) ||
         ((local_3c[0] == 0x34545844 || (local_3c[0] == 0x35545844)))) {
        local_20 = local_20 + 3 >> 2;
      }
      local_c = local_1c;
      if ((int)local_14 <= (int)local_1c) {
        local_c = local_14;
      }
      local_8 = 0;
      if (local_20 != 0) {
        do {
          puVar3 = local_10;
          puVar4 = local_18;
          for (uVar2 = local_c >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
            *puVar4 = *puVar3;
            puVar3 = puVar3 + 1;
            puVar4 = puVar4 + 1;
          }
          for (uVar2 = local_c & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
            *(undefined1 *)puVar4 = *(undefined1 *)puVar3;
            puVar3 = (undefined4 *)((int)puVar3 + 1);
            puVar4 = (undefined4 *)((int)puVar4 + 1);
          }
          local_10 = (undefined4 *)((int)local_10 + local_14);
          local_18 = (undefined4 *)((int)local_18 + local_1c);
          local_8 = local_8 + 1;
        } while (local_8 < local_20);
      }
      iVar1 = 0;
      (**(code **)(*(int *)param_2 + 0x38))(param_2);
    }
    (**(code **)(*(int *)param_1 + 0x38))(param_1);
  }
  return iVar1;
}
