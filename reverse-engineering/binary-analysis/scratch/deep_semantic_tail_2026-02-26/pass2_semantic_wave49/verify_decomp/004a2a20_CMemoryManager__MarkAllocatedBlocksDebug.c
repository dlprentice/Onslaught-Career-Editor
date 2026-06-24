/* address: 0x004a2a20 */
/* name: CMemoryManager__MarkAllocatedBlocksDebug */
/* signature: void __fastcall CMemoryManager__MarkAllocatedBlocksDebug(void * param_1) */


void __fastcall CMemoryManager__MarkAllocatedBlocksDebug(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;

  for (puVar1 = *(undefined4 **)param_1; puVar1 != (undefined4 *)0x0; puVar1 = (undefined4 *)*puVar1
      ) {
    iVar2 = puVar1[1];
    uVar3 = *(uint *)(iVar2 + 4);
    if ((uVar3 & 0xfffffff0) + 0x10 + iVar2 < (uint)(puVar1[2] + iVar2)) {
      do {
        if ((uVar3 & 1) != 0) {
          *(uint *)(iVar2 + 4) = uVar3 | 2;
        }
        iVar2 = iVar2 + 0x10 + (*(uint *)(iVar2 + 4) & 0xfffffff0);
        uVar3 = *(uint *)(iVar2 + 4);
      } while ((uVar3 & 0xfffffff0) + 0x10 + iVar2 < (uint)(puVar1[1] + puVar1[2]));
    }
  }
  return;
}
