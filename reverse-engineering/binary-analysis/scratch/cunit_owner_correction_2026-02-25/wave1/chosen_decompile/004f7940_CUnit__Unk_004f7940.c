/* address: 0x004f7940 */
/* name: CUnit__Unk_004f7940 */
/* signature: void __fastcall CUnit__Unk_004f7940(void * param_1) */


void __fastcall CUnit__Unk_004f7940(void *param_1)

{
  undefined2 uVar1;
  void *pvVar2;
  int iVar3;
  undefined4 *puVar4;
  int unaff_EDI;
  int local_c;
  undefined2 uStack_6;
  undefined2 uStack_2;

  local_c = 10;
  *(undefined4 *)((int)param_1 + 0x14) = 1;
  do {
    if (*(int *)((int)param_1 + 0x14) == 0) {
      return;
    }
    iVar3 = *(int *)((int)param_1 + 0xc);
    puVar4 = *(undefined4 **)((int)param_1 + 4);
    *(undefined4 *)((int)param_1 + 0x14) = 0;
    for (; iVar3 != 0; iVar3 = iVar3 + -1) {
      pvVar2 = (void *)*puVar4;
      uStack_6 = (undefined2)((uint)pvVar2 >> 0x10);
      uVar1 = *(undefined2 *)(puVar4 + 1);
      CUnit__Unk_004f7660(param_1,pvVar2,(int)CONCAT22(uVar1,uStack_6),unaff_EDI);
      CUnit__Unk_004f7660(param_1,(void *)CONCAT22(uVar1,uStack_6),CONCAT22(uStack_2,uVar1),
                          unaff_EDI);
      CUnit__Unk_004f7660(param_1,(void *)CONCAT22(uStack_2,uVar1),(int)pvVar2,unaff_EDI);
      puVar4 = (undefined4 *)((int)puVar4 + 6);
    }
    local_c = local_c + -1;
  } while (local_c != 0);
  return;
}
