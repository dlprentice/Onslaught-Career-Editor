/* address: 0x00574230 */
/* name: CFastVB__AssignDwordIfDestNotNull */
/* signature: void __cdecl CFastVB__AssignDwordIfDestNotNull(void * param_1, void * param_2) */


void __cdecl CFastVB__AssignDwordIfDestNotNull(void *param_1,void *param_2)

{
  if (param_1 != (void *)0x0) {
    *(undefined4 *)param_1 = *(undefined4 *)param_2;
  }
  return;
}
