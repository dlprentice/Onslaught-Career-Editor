/* address: 0x00574180 */
/* name: CTexture__Unk_00574180 */
/* signature: void __fastcall CTexture__Unk_00574180(void * param_1) */


void __fastcall CTexture__Unk_00574180(void *param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;

  puVar1 = *(undefined4 **)(*(int *)param_1 + 8);
  if (puVar1 == DAT_009d0c44) {
    iVar3 = *(int *)(*(int *)param_1 + 4);
    if (*(int *)param_1 == *(int *)(iVar3 + 8)) {
      do {
        *(int *)param_1 = iVar3;
        iVar3 = *(int *)(iVar3 + 4);
      } while (*(int *)param_1 == *(int *)(iVar3 + 8));
    }
    if (*(int *)(*(int *)param_1 + 8) != iVar3) {
      *(int *)param_1 = iVar3;
    }
    return;
  }
  for (puVar2 = (undefined4 *)*puVar1; puVar2 != DAT_009d0c44; puVar2 = (undefined4 *)*puVar2) {
    puVar1 = puVar2;
  }
  *(undefined4 **)param_1 = puVar1;
  return;
}
