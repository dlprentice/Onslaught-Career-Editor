/* address: 0x00569aa8 */
/* name: CRT__ParseFloatTextToFloat64 */
/* signature: void __cdecl CRT__ParseFloatTextToFloat64(void * param_1, int param_2) */


void __cdecl CRT__ParseFloatTextToFloat64(void *param_1,int param_2)

{
  undefined1 local_10 [12];

  CRT__ParseFloatTextToLongDouble();
  CRT__ConvertLongDoubleToFloat64(local_10,param_1);
  return;
}
