/* address: 0x004fce40 */
/* name: CUnitAI__Helper_004fce40 */
/* signature: int CUnitAI__Helper_004fce40(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnitAI__Helper_004fce40(void)

{
  int in_EAX;
  int in_ECX;

  if (*(int **)(in_ECX + 0x208) != (int *)0x0) {
    in_EAX = (**(code **)(**(int **)(in_ECX + 0x208) + 0x14))();
  }
  return in_EAX;
}
