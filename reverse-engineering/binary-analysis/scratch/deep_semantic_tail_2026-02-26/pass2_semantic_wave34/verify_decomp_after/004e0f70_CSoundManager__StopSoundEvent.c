/* address: 0x004e0f70 */
/* name: CSoundManager__StopSoundEvent */
/* signature: void __stdcall CSoundManager__StopSoundEvent(void * param_1) */


void CSoundManager__StopSoundEvent(void *param_1)

{
  if ((*(int *)((int)param_1 + 0x7c) == 1) && (*(int **)param_1 != (int *)0x0)) {
    (**(code **)(**(int **)param_1 + 0x18))(param_1);
  }
  if (-1 < *(int *)((int)param_1 + 4)) {
    CSoundManager__StopAndReleaseChannel(&DAT_00896988,param_1);
  }
  *(undefined1 *)((int)param_1 + 8) = 0;
  CGenericActiveReader__SetReader(param_1,(void *)0x0);
  return;
}
