/* address: 0x005ae780 */
/* name: CTexture__Helper_005ae780 */
/* signature: void __stdcall CTexture__Helper_005ae780(void * param_1) */


void CTexture__Helper_005ae780(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int unaff_ESI;

  puVar2 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x1c);
  iVar1 = *(int *)((int)param_1 + 0x54);
  *(undefined4 **)((int)param_1 + 0x1b4) = puVar2;
  *puVar2 = &LAB_005ae700;
  puVar2[2] = 0;
  puVar2[3] = 0;
  if (iVar1 != 0) {
    uVar3 = *(undefined4 *)((int)param_1 + 0x13c);
    puVar2[4] = uVar3;
    if (unaff_ESI != 0) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 4;
      (*(code *)*puVar2)(param_1);
      return;
    }
    uVar3 = (**(code **)(*(int *)((int)param_1 + 4) + 8))
                      (param_1,1,*(int *)((int)param_1 + 0x78) * *(int *)((int)param_1 + 0x70),uVar3
                      );
    puVar2[3] = uVar3;
  }
  return;
}
