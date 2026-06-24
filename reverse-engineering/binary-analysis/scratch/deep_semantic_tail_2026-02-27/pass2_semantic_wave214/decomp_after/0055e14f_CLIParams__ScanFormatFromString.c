/* address: 0x0055e14f */
/* name: CLIParams__ScanFormatFromString */
/* signature: void __cdecl CLIParams__ScanFormatFromString(void * param_1, int param_2) */


void __cdecl CLIParams__ScanFormatFromString(void *param_1,int param_2)

{
  void *local_24;
  size_t local_20;
  void *local_1c;
  undefined4 local_18;

  local_18 = 0x49;
  local_1c = param_1;
  local_24 = param_1;
  local_20 = _strlen(param_1);
  CRT__InputFormatCore((int)&local_24,(void *)param_2,&stack0x0000000c);
  return;
}
