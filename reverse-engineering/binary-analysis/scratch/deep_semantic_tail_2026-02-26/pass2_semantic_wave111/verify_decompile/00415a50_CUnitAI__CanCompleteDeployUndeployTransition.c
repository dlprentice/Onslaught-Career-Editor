/* address: 0x00415a50 */
/* name: CUnitAI__CanCompleteDeployUndeployTransition */
/* signature: int __fastcall CUnitAI__CanCompleteDeployUndeployTransition(void * param_1) */


int __fastcall CUnitAI__CanCompleteDeployUndeployTransition(void *param_1)

{
  int iVar1;

  iVar1 = (**(code **)(*(int *)param_1 + 0x10c))();
  if (iVar1 != 0) {
    return 0;
  }
  if (((*(int *)((int)param_1 + 0x168) != 0) || (*(int *)((int)param_1 + 0x214) == 0)) &&
     ((*(byte *)((int)param_1 + 0x2c) & 4) == 0)) {
    return 0;
  }
  return 1;
}
