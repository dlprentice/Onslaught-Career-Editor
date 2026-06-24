/* address: 0x00595430 */
/* name: CTexture__Helper_00595430 */
/* signature: void __stdcall CTexture__Helper_00595430(void * param_1, int param_2) */


void CTexture__Helper_00595430(void *param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;

  iVar1 = *(int *)((int)param_1 + 0x14);
  if (iVar1 != 100) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x14;
    puVar2[6] = iVar1;
    (*(code *)*puVar2)(param_1);
  }
  if (param_2 != 0) {
    CTexture__Helper_005952e0((int)param_1,0);
  }
  (**(code **)(*(int *)param_1 + 0x10))(param_1);
  (**(code **)(*(int *)((int)param_1 + 0x18) + 8))(param_1);
  CTexture__Helper_0059f2b0(param_1);
  (*(code *)**(undefined4 **)((int)param_1 + 0x154))(param_1);
  *(undefined4 *)((int)param_1 + 0xe8) = 0;
  *(uint *)((int)param_1 + 0x14) = (*(int *)((int)param_1 + 0xb0) != 0) + 0x65;
  return;
}
