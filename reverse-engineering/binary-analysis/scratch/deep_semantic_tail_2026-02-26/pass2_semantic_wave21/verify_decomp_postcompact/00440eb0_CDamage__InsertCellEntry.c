/* address: 0x00440eb0 */
/* name: CDamage__InsertCellEntry */
/* signature: int CDamage__InsertCellEntry(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDamage__InsertCellEntry(void)

{
  ushort *puVar1;
  ushort uVar2;
  ushort uVar3;
  int in_ECX;
  int iVar4;
  ushort in_stack_00000004;
  undefined1 in_stack_00000008;
  undefined1 in_stack_0000000c;
  undefined1 in_stack_00000010;

  iVar4 = *(int *)(in_ECX + 0x15884);
  uVar2 = *(ushort *)(in_ECX + 4 + iVar4 * 8);
  uVar3 = *(ushort *)(in_ECX + 6 + iVar4 * 8);
  puVar1 = (ushort *)(in_ECX + 4 + iVar4 * 8);
  if ((uVar2 & 0x8000) == 0) {
    *(ushort *)(in_ECX + 6 + (uint)uVar2 * 8) = uVar3;
  }
  else {
    *(ushort *)(in_ECX + 0x13884 + (uVar2 & 0xffff7fff) * 2) = uVar3;
  }
  *(ushort *)(in_ECX + 4 + (uint)uVar3 * 8) = uVar2;
  uVar2 = *(ushort *)(in_ECX + 0x13884 + (short)in_stack_00000004 * 2);
  puVar1[1] = uVar2;
  if (uVar2 != 0) {
    *(undefined2 *)(in_ECX + 4 + (uint)uVar2 * 8) = *(undefined2 *)(in_ECX + 0x15884);
  }
  *(undefined2 *)(in_ECX + 0x13884 + (short)in_stack_00000004 * 2) =
       *(undefined2 *)(in_ECX + 0x15884);
  *(undefined1 *)(puVar1 + 2) = in_stack_00000008;
  *(undefined1 *)((int)puVar1 + 5) = in_stack_0000000c;
  *puVar1 = in_stack_00000004 | 0x8000;
  *(undefined1 *)((int)puVar1 + 7) = in_stack_00000010;
  iVar4 = *(int *)(in_ECX + 0x15884) + 1;
  *(int *)(in_ECX + 0x15884) = iVar4;
  if (iVar4 == 10000) {
    iVar4 = *(int *)(in_ECX + 0x15888);
    *(int *)(in_ECX + 0x15884) = iVar4;
  }
  return iVar4;
}
