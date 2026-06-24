/* address: 0x00459aa0 */
/* name: CFEPMultiplayerStart__SubObj8848__TransitionNotification */
/* signature: void __thiscall CFEPMultiplayerStart__SubObj8848__TransitionNotification(void * this, int from_page) */


void __thiscall CFEPMultiplayerStart__SubObj8848__TransitionNotification(void *this,int from_page)

{
  int iVar1;
  undefined4 *puVar2;
  float fVar3;

  fVar3 = PLATFORM__GetSysTimeFloat();
  *(float *)((int)this + 0x3478) = fVar3;
  puVar2 = (undefined4 *)((int)this + 0x57c);
  for (iVar1 = 300; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  if ((from_page == 5) || (from_page == 6)) {
    *(undefined4 *)
     ((int)this + (*(int *)((int)this + 0x346c) + *(int *)((int)this + 0x3468) * 6) * 4 + 0x57c) =
         0x3f800000;
  }
  return;
}
