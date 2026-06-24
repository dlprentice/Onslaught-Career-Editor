/* address: 0x004fce80 */
/* name: CUnit__ForwardControllerQuery18 */
/* signature: int CUnit__ForwardControllerQuery18(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnit__ForwardControllerQuery18(void)

{
  int in_EAX;
  int in_ECX;

  if (*(int **)(in_ECX + 0x208) != (int *)0x0) {
    in_EAX = (**(code **)(**(int **)(in_ECX + 0x208) + 0x18))();
  }
  return in_EAX;
}
