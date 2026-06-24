/* address: 0x004f4430 */
/* name: CThing__Unk_004f4430 */
/* signature: int __fastcall CThing__Unk_004f4430(void * param_1) */


int __fastcall CThing__Unk_004f4430(void *param_1)

{
  if ((*(ushort *)((int)param_1 + 0x2c) & 4) == 0) {
    *(ushort *)((int)param_1 + 0x2c) = *(ushort *)((int)param_1 + 0x2c) | 4;
    (**(code **)(*(int *)param_1 + 0x38))();
    if (*(int *)((int)param_1 + 0x74) != 0) {
      IScript__Unk_00533660(*(int *)((int)param_1 + 0x74));
    }
    return 1;
  }
  return 0;
}
