/* address: 0x00459a60 */
/* name: CFEPMultiplayerStart__SubObj8848__ActiveNotification */
/* signature: void CFEPMultiplayerStart__SubObj8848__ActiveNotification(void * this, int from_page) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CFEPMultiplayerStart__SubObj8848__ActiveNotification(void *this,int from_page)

{
  int in_ECX;

  if ((this == (void *)0x5) || (this == (void *)0x6)) {
    *(undefined4 *)
     (in_ECX + 0x57c + (*(int *)(in_ECX + 0x346c) + *(int *)(in_ECX + 0x3468) * 6) * 4) = 0x3f800000
    ;
  }
  *(undefined4 *)(in_ECX + 0x347c) = 0;
  return;
}
