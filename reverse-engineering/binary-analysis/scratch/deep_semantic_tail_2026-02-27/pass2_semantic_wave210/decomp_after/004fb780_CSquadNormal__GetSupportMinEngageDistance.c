/* address: 0x004fb780 */
/* name: CSquadNormal__GetSupportMinEngageDistance */
/* signature: int CSquadNormal__GetSupportMinEngageDistance(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CSquadNormal__GetSupportMinEngageDistance(void)

{
  int extraout_EAX;
  int in_ECX;
  void *in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;

  if (*(void **)(in_ECX + 0x140) != (void *)0x0) {
    CUnit__ComputeMinBallisticTravelDistance
              (*(void **)(in_ECX + 0x140),in_stack_00000004,in_stack_00000008,in_stack_0000000c,
               in_stack_00000010);
    return extraout_EAX;
  }
  if (*(int *)(in_ECX + 0x144) != 0) {
    return *(int *)(*(int *)(in_ECX + 0x144) + 0x3d0);
  }
  return 0;
}
