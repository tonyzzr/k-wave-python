import pickle
import kwave.reconstruction.beamform as bf
import argparse


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Input file path')
  parser.add_argument('--input', type=str, help='Input file path', required=True)
  parser.add_argument('--f_number', type=float, help='f-number', required=True)
  parser.add_argument('--num_px_z', type=int, help='num_px_z', required=True)
  parser.add_argument('--imaging_depth', type=float, help='imaging_depth [m]', required=True)

  args = parser.parse_args()

  print(f'Input file path: {args.input}')
  # print(f'Output file path: {args.output}')
  input_path = args.input

  with open(input_path, 'rb') as f:
    channel_data = pickle.load(f)

  bf.beamform(
    channel_data,
    f_number = args.f_number,
    num_px_z = args.num_px_z,
    imaging_depth = args.imaging_depth,
  )