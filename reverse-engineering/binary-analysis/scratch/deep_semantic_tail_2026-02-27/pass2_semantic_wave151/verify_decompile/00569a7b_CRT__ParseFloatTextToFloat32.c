/* address: 0x00569a7b */
/* name: CRT__ParseFloatTextToFloat32 */
/* signature: void __cdecl CRT__ParseFloatTextToFloat32(void * param_1, int param_2) */


void __cdecl CRT__ParseFloatTextToFloat32(void *param_1,int param_2)

{
  undefined1 local_10 [12];

  CRT__ParseFloatTextToLongDouble();
  CRT__ConvertLongDoubleToFloat32(local_10,param_1);
  return;
}
