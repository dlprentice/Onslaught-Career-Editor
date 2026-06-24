/* address: 0x004d1fd0 */
/* name: CExplosionInitThing__PlayWingCloseAnimationOnce */
/* signature: void __fastcall CExplosionInitThing__PlayWingCloseAnimationOnce(void * param_1) */


void __fastcall CExplosionInitThing__PlayWingCloseAnimationOnce(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  if (*(int *)((int)param_1 + 0x27c) == 4) {
    iVar1 = *(int *)param_1;
    pvVar4 = (void *)0x1;
    pcVar3 = s_wingclose_0062442c;
    this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_wingclose_0062442c,1,0);
    iVar2 = FindAnimationIndex(this,(int)pcVar3,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar2);
    *(undefined4 *)((int)param_1 + 0x27c) = 3;
  }
  return;
}
