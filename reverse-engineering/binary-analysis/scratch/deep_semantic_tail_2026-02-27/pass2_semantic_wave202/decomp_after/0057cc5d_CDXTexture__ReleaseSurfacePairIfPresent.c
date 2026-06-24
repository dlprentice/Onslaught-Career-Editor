/* address: 0x0057cc5d */
/* name: CDXTexture__ReleaseSurfacePairIfPresent */
/* signature: void __fastcall CDXTexture__ReleaseSurfacePairIfPresent(void * param_1) */


void __fastcall CDXTexture__ReleaseSurfacePairIfPresent(void *param_1)

{
  if (*(undefined4 **)((int)param_1 + 4) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 4))(1);
  }
  if (*(undefined4 **)param_1 != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)param_1)(1);
  }
  return;
}
