/* address: 0x00562013 */
/* name: ControlsUI__ReadIntAndAdvance */
/* signature: int __cdecl ControlsUI__ReadIntAndAdvance(void * param_1) */


int __cdecl ControlsUI__ReadIntAndAdvance(void *param_1)

{
  *(int *)param_1 = *(int *)param_1 + 4;
  return *(int *)(*(int *)param_1 + -4);
}
