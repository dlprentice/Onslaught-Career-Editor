/* address: 0x004fcec0 */
/* name: CUnitAI__GetAttachedNodeReadyState */
/* signature: int CUnitAI__GetAttachedNodeReadyState(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnitAI__GetAttachedNodeReadyState(void)

{
  int in_EAX;
  int in_ECX;

  if (*(int **)(in_ECX + 0x208) != (int *)0x0) {
    in_EAX = (**(code **)(**(int **)(in_ECX + 0x208) + 0x1c))();
  }
  return in_EAX;
}
