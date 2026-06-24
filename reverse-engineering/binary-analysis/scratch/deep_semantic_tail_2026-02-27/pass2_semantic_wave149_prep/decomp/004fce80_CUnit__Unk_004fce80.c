/* address: 0x004fce80 */
/* name: CUnit__Unk_004fce80 */
/* signature: int CUnit__Unk_004fce80(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnit__Unk_004fce80(void)

{
  int in_EAX;
  int in_ECX;

  if (*(int **)(in_ECX + 0x208) != (int *)0x0) {
    in_EAX = (**(code **)(**(int **)(in_ECX + 0x208) + 0x18))();
  }
  return in_EAX;
}
