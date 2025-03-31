#include <astra/astra.hpp>
#include <opencv2/opencv.hpp>
#include <iostream>

int main(int argc, char** argv)
{
    // Initialize Astra
    astra::initialize();

    {
        // Create a StreamSet and a StreamReader
        astra::StreamSet streamSet;
        astra::StreamReader reader = streamSet.create_reader();

        // Start the color stream
        reader.stream<astra::ColorStream>().start();

        // (Optional) Load a Haar Cascade for face detection
        // Make sure the path is correct if you're doing face detection
        cv::CascadeClassifier faceCascade;
        faceCascade.load("haarcascade_frontalface_default.xml");

        while (true)
        {
            // Update Astra (this grabs the latest frames)
            astra_update();

            // Pull the latest overall frame from the reader
            astra::Frame frame = reader.get_latest_frame();

            // Get the ColorFrame from this Frame
            auto colorFrame = frame.get<astra::ColorFrame>();

            if (colorFrame.is_valid())
            {
                int width = colorFrame.width();
                int height = colorFrame.height();

                // Astra color data is astra::RgbPixel
                const astra::RgbPixel* data = colorFrame.data();

                // Create an OpenCV Mat (BGR) from the Astra RGB data
                cv::Mat image(height, width, CV_8UC3);
                for (int row = 0; row < height; ++row)
                {
                    for (int col = 0; col < width; ++col)
                    {
                        const astra::RgbPixel& p = data[row * width + col];
                        // Convert from RgbPixel (r,g,b) to OpenCV BGR
                        image.at<cv::Vec3b>(row, col) = cv::Vec3b(p.b, p.g, p.r);
                    }
                }

                // (Optional) Face detection
                if (!faceCascade.empty())
                {
                    cv::Mat gray;
                    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
                    std::vector<cv::Rect> faces;
                    faceCascade.detectMultiScale(gray, faces, 1.1, 5);

                    for (auto& face : faces)
                    {
                        cv::rectangle(image, face, cv::Scalar(0, 255, 0), 2);
                    }
                }

                // Show the color image
                cv::imshow("Astra Camera - Color", image);
            }

            // Press ESC to exit
            if (cv::waitKey(30) == 27)
            {
                break;
            }
        }
    }

    // Terminate Astra
    astra::terminate();
    return 0;
}
